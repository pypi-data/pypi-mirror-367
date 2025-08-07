"""
Data Processing Module

This module provides functionality for processing input data files,
including CSV and Excel files containing URLs for analysis.
"""

import os
import re
import concurrent.futures
import sys
from typing import Dict, List, Any, Optional, Callable, Tuple, Union

# Import memory management and optimization
from url_analyzer.utils.memory_management import (
    get_memory_profiler, optimize_dataframe, force_garbage_collection,
    configure_memory_optimization
)
from url_analyzer.utils.data_structures import (
    MemoryEfficientDict, MemoryEfficientList, optimize_dict, optimize_list
)
from url_analyzer.utils.lazy_loading import (
    lazy_import, pandas, numpy, get_lazy_component
)

# Assign lazy-loaded modules to standard names for compatibility with existing code
pd = pandas
np = numpy

# Optional imports for progress tracking
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Import progress tracking
from url_analyzer.utils.observers import (
    create_progress_tracker, ProgressTracker,
    create_pandas_progress_callback
)

# Import from other modules
from url_analyzer.core.classification import classify_url, get_base_domain
from url_analyzer.core.analysis import fetch_url_data, LIVE_SCAN_CACHE
from url_analyzer.utils.errors import (
    URLAnalyzerError, DataProcessingError, MissingColumnError, 
    InvalidFileFormatError, EmptyDataError, error_handler
)
from url_analyzer.utils.logging import get_logger
from url_analyzer.data.chunked_processing import process_file_in_chunks

# Create a logger for this module
logger = get_logger(__name__)

# Default threshold for using chunked processing (in rows)
# Files larger than this will use chunked processing by default
CHUNKED_PROCESSING_THRESHOLD = 100000  # 100K rows

# Check for psutil availability
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, some memory monitoring features will be disabled")

# Initialize memory profiler
memory_profiler = get_memory_profiler()

# Register callbacks for memory limit exceeded
def _handle_memory_limit_exceeded():
    """Handle the case where memory usage exceeds the configured limit."""
    logger.warning("Memory limit exceeded during data processing, applying graceful degradation")
    # Force garbage collection
    force_garbage_collection()
    # Switch to aggressive memory optimization
    configure_memory_optimization(2)

# Register the callback if not already registered
memory_profiler.register_limit_callback(_handle_memory_limit_exceeded)


def validate_file_exists(file_path: str) -> str:
    """
    Validates that the file exists and is a valid file path.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Validated file path
        
    Raises:
        FileNotFoundError: If the file does not exist
        PathValidationError: If the path is invalid
        ValidationError: If the file path is not a string
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_file_path
    from url_analyzer.utils.errors import ValidationError, PathValidationError
    
    try:
        # Validate the file path
        validated_path = validate_file_path(
            file_path, 
            must_exist=True, 
            error_message=f"Invalid file path: {file_path}"
        )
        
        logger.debug(f"Validated file path: {validated_path}")
        return validated_path
        
    except ValidationError as e:
        # Log the error
        error_msg = str(e)
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Re-raise as FileNotFoundError if the file doesn't exist
        if isinstance(e, PathValidationError) and "does not exist" in error_msg:
            raise FileNotFoundError(error_msg)
        
        # Otherwise, re-raise the original exception
        raise


def determine_chunked_processing(
    file_path: str, 
    use_chunked_processing: Optional[bool] = None
) -> bool:
    """
    Determines whether to use chunked processing based on file size and format.
    
    Args:
        file_path: Path to the file to process
        use_chunked_processing: Whether to use chunked processing (if None, determined automatically)
        
    Returns:
        Boolean indicating whether to use chunked processing
    """
    if use_chunked_processing is not None:
        return use_chunked_processing
    
    # Auto-detect based on file size and format
    file_size = os.path.getsize(file_path)
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # For CSV files, estimate the number of rows based on file size
    # This is a rough estimate - 100 bytes per row is a conservative estimate
    if file_ext == '.csv':
        estimated_rows = file_size / 100  # Rough estimate: 100 bytes per row
        return estimated_rows > CHUNKED_PROCESSING_THRESHOLD
    # For Excel files, we need to read the file to get the number of rows
    elif file_ext in ('.xlsx', '.xls'):
        try:
            # Just read the number of rows without loading the data
            if file_ext == '.xlsx':
                import openpyxl
                wb = openpyxl.load_workbook(file_path, read_only=True)
                sheet = wb.active
                row_count = sheet.max_row
                wb.close()
            else:  # .xls
                import xlrd
                wb = xlrd.open_workbook(file_path, on_demand=True)
                sheet = wb.sheet_by_index(0)
                row_count = sheet.nrows
                wb.release_resources()
            return row_count > CHUNKED_PROCESSING_THRESHOLD
        except Exception:
            # If we can't determine the row count, use chunked processing for files > 10MB
            return file_size > 10 * 1024 * 1024  # 10MB
    else:
        # For other file types, don't use chunked processing
        return False


def log_memory_usage(message: str) -> Optional[float]:
    """
    Logs memory usage if psutil is available.
    
    Args:
        message: Message to log with memory usage
        
    Returns:
        Current memory usage in MB or None if psutil is not available
    """
    if PSUTIL_AVAILABLE:
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024  # in MB
        logger.info(f"{message}: {memory_mb:.2f} MB")
        return memory_mb
    return None


def load_dataframe(file_path: str) -> pd.DataFrame:
    """
    Loads a DataFrame from a file.
    
    Args:
        file_path: Path to the file to load
        
    Returns:
        Loaded DataFrame
        
    Raises:
        InvalidFileFormatError: If the file format is invalid or cannot be parsed
        EmptyDataError: If the file is empty
        FileNotFoundError: If the file does not exist
        PathValidationError: If the path is invalid
        ValidationError: If the file path is not a string
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_enum
    from url_analyzer.utils.errors import ValidationError, InvalidFileFormatError, PathValidationError
    
    # Use memory profiler to track memory usage during loading
    from url_analyzer.utils.memory_profiler import ProfileMemoryBlock
    
    try:
        # Validate that the file exists and get the validated path
        validated_path = validate_file_exists(file_path)
        
        # Get the file extension and validate it
        file_ext = os.path.splitext(validated_path)[1].lower()
        
        try:
            # Validate that the file extension is supported
            validate_enum(
                file_ext, 
                ['.csv', '.xlsx', '.xls'], 
                error_message=f"Unsupported file format: {file_ext}"
            )
        except ValidationError as e:
            error_msg = str(e)
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise InvalidFileFormatError(error_msg)
        
        # Load the DataFrame based on the file extension
        logger.info(f"Loading data from file: {os.path.basename(validated_path)}")
        
        # Track memory usage during file loading
        with ProfileMemoryBlock(f"load_file_{os.path.basename(validated_path)}"):
            # Log memory usage before loading
            memory_before = log_memory_usage("Memory usage before loading file")
            
            # Determine if we should use chunked loading based on file size
            file_size_mb = os.path.getsize(validated_path) / (1024 * 1024)
            use_chunked = file_size_mb > 100  # Use chunked loading for files > 100 MB
            
            if file_ext == '.csv' and use_chunked:
                # For large CSV files, use chunked loading
                logger.info(f"Using chunked loading for large CSV file ({file_size_mb:.1f} MB)")
                # Read the file in chunks and concatenate
                chunks = []
                for chunk in pd.read_csv(validated_path, chunksize=50000, on_bad_lines='skip'):
                    # Optimize each chunk for memory efficiency
                    chunk = optimize_dataframe(chunk)
                    chunks.append(chunk)
                df = pd.concat(chunks, ignore_index=True)
                logger.debug(f"Loaded CSV file with {len(df)} rows and {len(df.columns)} columns")
            elif file_ext == '.csv':
                # For smaller CSV files, load normally
                df = pd.read_csv(validated_path, on_bad_lines='skip')
                logger.debug(f"Loaded CSV file with {len(df)} rows and {len(df.columns)} columns")
            else:  # .xlsx or .xls
                # Excel files are loaded entirely into memory
                df = pd.read_excel(validated_path)
                logger.debug(f"Loaded Excel file with {len(df)} rows and {len(df.columns)} columns")
            
            # Log memory usage after loading
            memory_after = log_memory_usage("Memory usage after loading file")
            if memory_before is not None and memory_after is not None:
                memory_diff = memory_after - memory_before
                logger.info(f"Memory usage increased by {memory_diff:.2f} MB during file loading")
                
                # If memory usage is high, force garbage collection
                if memory_diff > 500:  # More than 500 MB
                    logger.warning("High memory usage detected, forcing garbage collection")
                    force_garbage_collection()
        
        # Check if DataFrame is empty
        if df.empty:
            error_msg = f"File is empty: {os.path.basename(validated_path)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise EmptyDataError(error_msg)
        
        # Clean column names
        original_columns = df.columns.tolist()
        df.columns = [re.sub(r'[^a-zA-Z0-9_]', '', col.replace(' ', '_')) for col in df.columns]
        
        # Log column name changes
        for i, (orig, new) in enumerate(zip(original_columns, df.columns)):
            if orig != new:
                logger.debug(f"Column name cleaned: '{orig}' -> '{new}'")
        
        # Optimize the DataFrame for memory efficiency
        logger.info("Optimizing DataFrame for memory efficiency")
        df = optimize_dataframe(df)
        
        return df
        
    except pd.errors.ParserError as e:
        error_msg = f"Error parsing file {os.path.basename(file_path)}: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise InvalidFileFormatError(error_msg, {"original_error": str(e)})
    except (FileNotFoundError, PathValidationError, ValidationError) as e:
        # Re-raise these exceptions as they're already handled appropriately
        raise
    except Exception as e:
        error_msg = f"Error reading file {os.path.basename(file_path)}: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise DataProcessingError(error_msg, {"original_error": str(e)})


def validate_required_columns(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """
    Validates that the DataFrame contains required columns.
    
    Args:
        df: DataFrame to validate
        file_path: Path to the file (for error messages)
        
    Returns:
        The validated DataFrame
        
    Raises:
        MissingColumnError: If a required column is missing
        ValidationError: If the DataFrame is not valid
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_type
    from url_analyzer.utils.errors import ValidationError, MissingColumnError
    
    try:
        # Validate that df is a DataFrame
        validate_type(df, pd.DataFrame, error_message="Input must be a pandas DataFrame")
        
        # Define required columns
        required_columns = ['Domain_name']
        
        # Check if all required columns are present
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            error_msg = f"Required column(s) {', '.join(missing_columns)} not found in {os.path.basename(file_path)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise MissingColumnError(
                error_msg, 
                {
                    "file": os.path.basename(file_path), 
                    "missing_columns": missing_columns
                }
            )
        
        # Log successful validation
        logger.debug(f"Validated required columns in {os.path.basename(file_path)}")
        
        # Return the validated DataFrame
        return df
        
    except ValidationError as e:
        # Re-raise ValidationError as it's already properly formatted
        raise
    except Exception as e:
        # Log and re-raise other exceptions
        error_msg = f"Error validating DataFrame columns: {str(e)}"
        logger.error(error_msg)
        raise ValidationError(error_msg)


def classify_urls_with_progress(
    df: pd.DataFrame, 
    compiled_patterns: Dict[str, Any], 
    file_path: str
) -> pd.DataFrame:
    """
    Classifies URLs in the DataFrame with progress tracking.
    
    Args:
        df: DataFrame containing URLs to classify
        compiled_patterns: Dictionary of compiled regex patterns
        file_path: Path to the file (for logging)
        
    Returns:
        DataFrame with URL_Category and Is_Sensitive columns added
        
    Raises:
        DataProcessingError: If there's an error classifying URLs
    """
    try:
        logger.info(f"Classifying URLs in {os.path.basename(file_path)}")
        url_column = 'Domain_name'
        
        # Create a progress tracker for URL classification
        url_count = len(df)
        progress_tracker = create_progress_tracker(
            total=url_count,
            description="Classifying URLs",
            # Use tqdm if available, otherwise use console
            tqdm=TQDM_AVAILABLE,
            console=not TQDM_AVAILABLE
        )
        
        # Start progress tracking
        progress_tracker.start(url_count, "Classifying URLs")
        
        # Process URLs with progress tracking
        results = []
        for i, url in enumerate(df[url_column]):
            result = classify_url(url, compiled_patterns)
            results.append(result)
            # Update progress every 10 items to avoid overhead
            if i % 10 == 0 or i == url_count - 1:
                progress_tracker.update(i + 1)
        
        # Finish progress tracking
        progress_tracker.finish()
        
        df['URL_Category'] = [res[0] for res in results]
        df['Is_Sensitive'] = [res[1] for res in results]
        return df
    except Exception as e:
        error_msg = f"Error classifying URLs in {os.path.basename(file_path)}: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise DataProcessingError(error_msg, {"original_error": str(e)})


def extract_base_domains_with_progress(
    df: pd.DataFrame, 
    file_path: str
) -> pd.DataFrame:
    """
    Extracts base domains from URLs in the DataFrame with progress tracking.
    
    Args:
        df: DataFrame containing URLs to process
        file_path: Path to the file (for logging)
        
    Returns:
        DataFrame with Base_Domain column added
        
    Raises:
        DataProcessingError: If there's an error extracting base domains
    """
    try:
        logger.info(f"Extracting base domains in {os.path.basename(file_path)}")
        url_column = 'Domain_name'
        
        # Create a progress tracker for base domain extraction
        url_count = len(df)
        progress_tracker = create_progress_tracker(
            total=url_count,
            description="Extracting Base Domains",
            # Use tqdm if available, otherwise use console
            tqdm=TQDM_AVAILABLE,
            console=not TQDM_AVAILABLE
        )
        
        # Start progress tracking
        progress_tracker.start(url_count, "Extracting Base Domains")
        
        # Process URLs with progress tracking
        base_domains = []
        for i, url in enumerate(df[url_column]):
            base_domain = get_base_domain(url)
            base_domains.append(base_domain)
            # Update progress every 10 items to avoid overhead
            if i % 10 == 0 or i == url_count - 1:
                progress_tracker.update(i + 1)
        
        # Finish progress tracking
        progress_tracker.finish()
        
        df['Base_Domain'] = base_domains
        return df
    except Exception as e:
        error_msg = f"Error extracting base domains in {os.path.basename(file_path)}: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise DataProcessingError(error_msg, {"original_error": str(e)})


def perform_live_scan(
    df: pd.DataFrame, 
    cli_args: Any, 
    file_path: str
) -> pd.DataFrame:
    """
    Performs a live scan on uncategorized URLs in the DataFrame.
    
    Args:
        df: DataFrame containing URLs to scan
        cli_args: Command-line arguments
        file_path: Path to the file (for logging)
        
    Returns:
        DataFrame with Notes column updated with scan results
    """
    if not cli_args.live_scan:
        return df
    
    url_column = 'Domain_name'
    df['Notes'] = ''  # Initialize Notes column
    
    try:
        uncategorized_urls = df[df['URL_Category'] == 'Uncategorized'][url_column].dropna().unique().tolist()
        if not uncategorized_urls:
            return df
        
        logger.info(f"Performing live scan on {len(uncategorized_urls)} URLs")
        print(f"⚡ Performing live scan on {len(uncategorized_urls)} unique uncategorized URLs...")
        
        # Get configuration
        from url_analyzer.config.manager import load_config
        from url_analyzer.utils.concurrency import create_thread_pool_executor
        config = load_config()
        
        # Create a progress tracker for live scanning
        url_count = len(uncategorized_urls)
        progress_tracker = create_progress_tracker(
            total=url_count,
            description="Live Scanning",
            # Use tqdm if available, otherwise use console
            tqdm=TQDM_AVAILABLE,
            console=not TQDM_AVAILABLE
        )
        
        # Start progress tracking
        progress_tracker.start(url_count, "Live Scanning")
        
        # Create thread pool executor with adaptive settings
        # Use "io" operation type since URL scanning is I/O-bound
        with create_thread_pool_executor(config, operation_type="io") as executor:
            future_map = {
                executor.submit(fetch_url_data, url, cli_args.summarize, config): url 
                for url in uncategorized_urls
            }
            
            # Process completed futures with progress tracking
            completed_count = 0
            for future in concurrent.futures.as_completed(future_map):
                try:
                    _, scan_result = future.result()
                    LIVE_SCAN_CACHE[future_map[future]] = scan_result
                except Exception as e:
                    logger.warning(f"Error scanning URL {future_map[future]}: {e}")
                    # Continue with other URLs even if one fails
                
                # Update progress
                completed_count += 1
                progress_tracker.update(completed_count)
        
        # Finish progress tracking
        progress_tracker.finish()

        # Add scan results to Notes column
        def get_note(row):
            if row['URL_Category'] == 'Uncategorized':
                data = LIVE_SCAN_CACHE.get(row[url_column], {})
                title = data.get('title', '')
                summary = data.get('summary', '')
                return f"Title: {title}" + (f" | Summary: {summary}" if summary else "")
            return ''

        df['Notes'] = df.apply(get_note, axis=1)
        return df
    except Exception as e:
        # Log the error but don't fail the entire process
        error_msg = f"Error during live scan in {os.path.basename(file_path)}: {e}"
        logger.error(error_msg)
        print(f"⚠️ {error_msg}")
        # Continue processing without live scan results
        return df


def process_file(
    file_path: str, 
    compiled_patterns: Dict[str, Any], 
    cli_args: Any,
    use_chunked_processing: Optional[bool] = None,
    chunk_size: int = 10000
) -> pd.DataFrame:
    """
    Reads, processes, and saves a single file, returning its DataFrame.
    
    This function automatically determines whether to use chunked processing
    based on the file size, unless explicitly specified with use_chunked_processing.
    
    Args:
        file_path: Path to the file to process
        compiled_patterns: Dictionary of compiled regex patterns or ClassificationStrategy
        cli_args: Command-line arguments
        use_chunked_processing: Whether to use chunked processing (if None, determined automatically)
        chunk_size: Number of rows to process in each chunk (only used with chunked processing)
        
    Returns:
        Processed DataFrame
        
    Raises:
        FileNotFoundError: If the file does not exist
        InvalidFileFormatError: If the file format is invalid or cannot be parsed
        MissingColumnError: If a required column is missing from the data
        DataProcessingError: If there's an error processing the data
        ValidationError: If any input parameters are invalid
        PathValidationError: If the file path is invalid
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_string, validate_dict, validate_integer, validate_type
    from url_analyzer.utils.errors import ValidationError, DataProcessingError
    
    # Use memory profiler to track memory usage during processing
    from url_analyzer.utils.memory_profiler import ProfileMemoryBlock
    
    try:
        # Validate input parameters
        validate_string(file_path, allow_empty=False, error_message="File path cannot be empty")
        validate_dict(compiled_patterns, error_message="Compiled patterns must be a dictionary")
        
        if use_chunked_processing is not None:
            validate_type(use_chunked_processing, bool, error_message="use_chunked_processing must be a boolean")
        
        validate_integer(chunk_size, min_value=1, error_message="Chunk size must be a positive integer")
        
        # Log the start of processing
        logger.info(f"Processing file: {os.path.basename(file_path)}")
        
        # Validate file exists and get the validated path
        validated_path = validate_file_exists(file_path)
        
        # Track memory usage during the entire processing
        with ProfileMemoryBlock(f"process_file_{os.path.basename(validated_path)}"):
            # Determine whether to use chunked processing
            use_chunked = determine_chunked_processing(validated_path, use_chunked_processing)
            
            # Log memory usage before processing
            memory_before = log_memory_usage("Memory usage before processing")
            
            # Optimize compiled patterns using memory pooling
            if isinstance(compiled_patterns, dict):
                compiled_patterns = optimize_dict(compiled_patterns)
            
            # Use chunked processing if determined
            if use_chunked:
                logger.info(f"Using chunked processing for {os.path.basename(validated_path)} with chunk size {chunk_size}")
                print(f"\n--- Processing: {os.path.basename(validated_path)} (chunked mode) ---")
                
                # Process file in chunks with memory optimization
                result_df = process_file_in_chunks(validated_path, compiled_patterns, cli_args, chunk_size)
                
                # Force garbage collection after chunked processing
                force_garbage_collection()
                
                return result_df
            
            # Standard processing (load entire file)
            print(f"\n--- Processing: {os.path.basename(validated_path)} ---")
            
            # Load the DataFrame with memory optimization
            df = load_dataframe(validated_path)
            
            # Log memory usage after loading
            if PSUTIL_AVAILABLE and memory_before is not None:
                memory_after_load = log_memory_usage("Memory usage after loading file")
                if memory_after_load is not None:
                    memory_delta = memory_after_load - memory_before
                    logger.info(f"Memory delta: {memory_delta:.2f} MB")
                    
                    # If memory usage is high, switch to aggressive optimization
                    if memory_delta > 1000:  # More than 1 GB
                        logger.warning("High memory usage detected, switching to aggressive optimization")
                        configure_memory_optimization(2)  # Aggressive optimization
                        
                        # Force garbage collection to free memory
                        force_garbage_collection()
            
            # Validate required columns and get the validated DataFrame
            df = validate_required_columns(df, validated_path)
            
            # Use memory-efficient data structures for intermediate results
            results_list = MemoryEfficientList()
            
            # Classify URLs with progress tracking and memory optimization
            logger.info(f"Classifying URLs in {os.path.basename(validated_path)}")
            url_column = 'Domain_name'
            
            # Create a progress tracker for URL classification
            url_count = len(df)
            progress_tracker = create_progress_tracker(
                total=url_count,
                description="Classifying URLs",
                tqdm=TQDM_AVAILABLE,
                console=not TQDM_AVAILABLE
            )
            
            # Start progress tracking
            progress_tracker.start(url_count, "Classifying URLs")
            
            # Process URLs with progress tracking
            for i, url in enumerate(df[url_column]):
                result = classify_url(url, compiled_patterns)
                results_list.append(result)
                # Update progress every 10 items to avoid overhead
                if i % 10 == 0 or i == url_count - 1:
                    progress_tracker.update(i + 1)
            
            # Finish progress tracking
            progress_tracker.finish()
            
            # Apply results to DataFrame
            df['URL_Category'] = [res[0] for res in results_list]
            df['Is_Sensitive'] = [res[1] for res in results_list]
            
            # Extract base domains with memory optimization
            logger.info(f"Extracting base domains in {os.path.basename(validated_path)}")
            
            # Create a progress tracker for base domain extraction
            progress_tracker = create_progress_tracker(
                total=url_count,
                description="Extracting Base Domains",
                tqdm=TQDM_AVAILABLE,
                console=not TQDM_AVAILABLE
            )
            
            # Start progress tracking
            progress_tracker.start(url_count, "Extracting Base Domains")
            
            # Use memory-efficient list for base domains
            base_domains = MemoryEfficientList()
            
            # Process URLs with progress tracking
            for i, url in enumerate(df[url_column]):
                base_domain = get_base_domain(url)
                base_domains.append(base_domain)
                # Update progress every 10 items to avoid overhead
                if i % 10 == 0 or i == url_count - 1:
                    progress_tracker.update(i + 1)
            
            # Finish progress tracking
            progress_tracker.finish()
            
            # Apply base domains to DataFrame
            df['Base_Domain'] = base_domains
            
            # Perform live scan if requested
            df = perform_live_scan(df, cli_args, validated_path)
            
            # Optimize DataFrame for memory efficiency
            df = optimize_dataframe(df)
            
            # Log memory usage after processing
            if PSUTIL_AVAILABLE and memory_before is not None:
                memory_after = log_memory_usage("Memory usage after processing")
                if memory_after is not None:
                    logger.info(f"Total memory delta: {memory_after - memory_before:.2f} MB")
            
            # Log successful processing
            logger.info(f"Successfully processed file: {os.path.basename(validated_path)}")
            
            return df
        
    except (FileNotFoundError, InvalidFileFormatError, MissingColumnError, ValidationError) as e:
        # These exceptions are already properly formatted and logged
        raise
    except Exception as e:
        # Log and re-raise other exceptions as DataProcessingError
        error_msg = f"Error processing file {os.path.basename(file_path)}: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Force garbage collection to free memory
        force_garbage_collection()
        
        raise DataProcessingError(error_msg, {"original_error": str(e)})


def process_files(
    files_to_process: List[str], 
    compiled_patterns: Dict[str, Any], 
    cli_args: Any
) -> Tuple[List[pd.DataFrame], str]:
    """
    Process multiple files and return a list of processed DataFrames.
    
    Args:
        files_to_process: List of file paths to process
        compiled_patterns: Dictionary of compiled regex patterns or ClassificationStrategy
        cli_args: Command-line arguments
        
    Returns:
        Tuple of (list of processed DataFrames, report path)
        
    Raises:
        DataProcessingError: If there's an error processing the files
        EmptyDataError: If no valid data is found after processing
        ValidationError: If any input parameters are invalid
        FileNotFoundError: If a file does not exist
        InvalidFileFormatError: If a file format is invalid
        MissingColumnError: If required columns are missing
    """
    # Import validation utilities
    from url_analyzer.utils.validation import validate_list, validate_dict, validate_integer
    from url_analyzer.utils.errors import ValidationError, EmptyDataError, DataProcessingError
    
    # Use memory profiler to track memory usage during processing
    from url_analyzer.utils.memory_profiler import ProfileMemoryBlock
    
    try:
        # Validate input parameters
        validate_list(files_to_process, min_length=1, error_message="Files to process cannot be empty")
        validate_dict(compiled_patterns, error_message="Compiled patterns must be a dictionary")
        
        # Track memory usage during the entire processing
        with ProfileMemoryBlock("process_files"):
            # Log the start of processing
            logger.info(f"Processing {len(files_to_process)} files")
            
            # Get chunked processing parameters from command-line arguments
            use_chunked_processing = getattr(cli_args, 'chunked', None)
            chunk_size = getattr(cli_args, 'chunk_size', 10000)
            
            # Validate chunk_size if provided
            if chunk_size is not None:
                validate_integer(chunk_size, min_value=1, error_message="Chunk size must be a positive integer")
            
            # Log processing mode
            if use_chunked_processing is True:
                logger.info(f"Using chunked processing mode with chunk size {chunk_size}")
            elif use_chunked_processing is False:
                logger.info("Using standard processing mode (no chunking)")
            else:
                logger.info(f"Using automatic processing mode selection with threshold {CHUNKED_PROCESSING_THRESHOLD} rows")
            
            # Optimize compiled patterns using memory pooling
            if isinstance(compiled_patterns, dict):
                compiled_patterns = optimize_dict(compiled_patterns)
            
            # Use memory-efficient list for storing DataFrames
            all_dfs = MemoryEfficientList()
            processed_files = 0
            skipped_files = 0
            
            # Log memory usage before processing
            memory_before = log_memory_usage("Memory usage before processing files")
            
            # Process each file
            for file_index, file in enumerate(files_to_process):
                try:
                    logger.info(f"Processing file {file_index + 1}/{len(files_to_process)}: {os.path.basename(file)}")
                    
                    # Process the file with memory optimization
                    df = process_file(
                        file, 
                        compiled_patterns, 
                        cli_args,
                        use_chunked_processing=use_chunked_processing,
                        chunk_size=chunk_size
                    )
                    
                    # Append the DataFrame to the list
                    all_dfs.append(df)
                    processed_files += 1
                    
                    logger.info(f"Successfully processed file {file_index + 1}/{len(files_to_process)}")
                    
                    # Check memory usage after processing each file
                    if PSUTIL_AVAILABLE and memory_before is not None:
                        current_memory = log_memory_usage(f"Memory after processing file {file_index + 1}")
                        if current_memory is not None:
                            memory_delta = current_memory - memory_before
                            logger.info(f"Memory delta: {memory_delta:.2f} MB")
                            
                            # If memory usage is high, take action to reduce it
                            if memory_delta > 2000:  # More than 2 GB
                                logger.warning("High memory usage detected, applying memory optimization")
                                
                                # Switch to aggressive memory optimization
                                configure_memory_optimization(2)
                                
                                # Force garbage collection to free memory
                                force_garbage_collection()
                                
                                # Log memory usage after optimization
                                optimized_memory = log_memory_usage("Memory after optimization")
                                if optimized_memory is not None:
                                    logger.info(f"Memory reduced by {current_memory - optimized_memory:.2f} MB")
                    
                except (FileNotFoundError, InvalidFileFormatError, EmptyDataError, MissingColumnError, ValidationError) as e:
                    # Log the error but continue with other files
                    logger.warning(f"Skipping file {file}: {e}")
                    print(f"⚠️ Skipping file {os.path.basename(file)}: {e}")
                    skipped_files += 1
                except Exception as e:
                    # Log unexpected errors but continue with other files
                    error_msg = f"Unexpected error processing file {file}: {e}"
                    logger.error(error_msg)
                    print(f"❌ {error_msg}")
                    skipped_files += 1
                    
                    # Force garbage collection to free memory
                    force_garbage_collection()
            
            # Check if we have any valid DataFrames
            if not all_dfs:
                error_msg = f"No valid data to process after attempting all files. Skipped {skipped_files} files."
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                raise EmptyDataError(error_msg)
            
            # Determine report path
            if hasattr(cli_args, 'aggregate') and cli_args.aggregate:
                # Use the first file as the base for the aggregated report name
                report_path = f"{os.path.splitext(files_to_process[0])[0]}_aggregated_report.html"
                logger.info(f"Using aggregated report path: {report_path}")
            else:
                # Use the last processed file as the base for the report name
                report_path = f"{os.path.splitext(files_to_process[-1])[0]}_report.html"
                logger.info(f"Using single file report path: {report_path}")
            
            # Log memory usage after processing all files
            if PSUTIL_AVAILABLE and memory_before is not None:
                final_memory = log_memory_usage("Memory usage after processing all files")
                if final_memory is not None:
                    logger.info(f"Total memory delta: {final_memory - memory_before:.2f} MB")
            
            # Log summary
            logger.info(f"Successfully processed {processed_files} files, skipped {skipped_files} files")
            print(f"✅ Successfully processed {processed_files} files, skipped {skipped_files} files")
            
            # Force garbage collection before returning
            force_garbage_collection()
            
            return list(all_dfs), report_path
        
    except ValidationError as e:
        # These exceptions are already properly formatted and logged
        raise
    except EmptyDataError as e:
        # Re-raise EmptyDataError as it's already properly formatted
        raise
    except Exception as e:
        # Log and re-raise other exceptions as DataProcessingError
        error_msg = f"Error processing files: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Force garbage collection to free memory
        force_garbage_collection()
        
        raise DataProcessingError(error_msg, {"original_error": str(e)})


def print_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Prints a final summary dashboard to the console and returns stats.
    
    Args:
        df: Processed DataFrame
        
    Returns:
        Dictionary of statistics
        
    Raises:
        DataProcessingError: If there's an error processing the summary
        EmptyDataError: If the DataFrame is empty
    """
    # Use memory profiler to track memory usage during summary generation
    from url_analyzer.utils.memory_profiler import ProfileMemoryBlock
    
    try:
        # Validate input
        if df is None:
            error_msg = "Cannot generate summary: DataFrame is None"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise DataProcessingError(error_msg)
            
        if df.empty:
            error_msg = "Cannot generate summary: DataFrame is empty"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise EmptyDataError(error_msg)
        
        # Track memory usage during summary generation
        with ProfileMemoryBlock("print_summary"):
            # Log memory usage before summary generation
            memory_before = log_memory_usage("Memory usage before summary generation")
            
            # Calculate statistics
            total_urls = len(df)
            
            # Check for required columns with clear error messages
            if 'Is_Sensitive' not in df.columns:
                logger.warning("Column 'Is_Sensitive' not found in DataFrame, using 0 for sensitive count")
                total_sensitive = 0
            else:
                # Use efficient calculation for sensitive count
                total_sensitive = int(df['Is_Sensitive'].sum())
                
            if 'URL_Category' not in df.columns:
                logger.warning("Column 'URL_Category' not found in DataFrame, using empty dict for category counts")
                category_counts = {}
            else:
                # Use memory-efficient dictionary for category counts
                category_counts_df = df['URL_Category'].value_counts()
                category_counts = MemoryEfficientDict()
                
                # Process in smaller batches to reduce memory usage
                for category, count in category_counts_df.items():
                    category_counts[category] = int(count)
            
            # Log memory usage after calculations
            if PSUTIL_AVAILABLE and memory_before is not None:
                memory_after_calc = log_memory_usage("Memory usage after calculations")
                if memory_after_calc is not None:
                    logger.debug(f"Memory delta for calculations: {memory_after_calc - memory_before:.2f} MB")
            
            # Log summary information
            logger.info(f"Generated summary for {total_urls} URLs ({total_sensitive} sensitive)")
            
            # Print summary to console
            print(f"\n\n---  Final Analysis Summary ---")
            print(f"Total URLs Analyzed: {total_urls}")
            print(f"Total Sensitive URLs Detected: {total_sensitive}")
            print("\nCategory Breakdown:")
            
            # Use memory-efficient sorting and iteration
            sorted_categories = sorted(category_counts.items())
            
            for cat, count in sorted_categories:
                percentage = (count / total_urls) * 100 if total_urls > 0 else 0
                print(f"  - {cat}: {count} ({percentage:.1f}%)")
            
            print("-" * 30)
            
            # Create a regular dictionary for the return value (for compatibility)
            result_dict = {
                'total': total_urls, 
                'sensitive': total_sensitive,
                'category_counts': dict(category_counts)
            }
            
            # Log memory usage after summary generation
            if PSUTIL_AVAILABLE and memory_before is not None:
                memory_after = log_memory_usage("Memory usage after summary generation")
                if memory_after is not None:
                    logger.debug(f"Total memory delta for summary: {memory_after - memory_before:.2f} MB")
            
            # Force garbage collection to free memory
            force_garbage_collection()
            
            return result_dict
            
    except (DataProcessingError, EmptyDataError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Error generating summary: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
        # Force garbage collection to free memory
        force_garbage_collection()
        
        raise DataProcessingError(error_msg, {"original_error": str(e)})