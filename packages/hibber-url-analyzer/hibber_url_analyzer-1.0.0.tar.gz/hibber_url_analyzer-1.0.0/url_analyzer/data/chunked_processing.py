"""
Chunked Processing Module

This module provides functionality for processing large data files in chunks,
improving memory efficiency and performance for large datasets.
"""

import os
import re
import pandas as pd
import concurrent.futures
from typing import Dict, List, Any, Optional, Callable, Tuple, Union, Iterator, Generator

# Optional imports for progress tracking
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

# Import from other modules
from url_analyzer.core.classification import classify_url, get_base_domain
from url_analyzer.core.analysis import fetch_url_data, LIVE_SCAN_CACHE
from url_analyzer.utils.errors import (
    URLAnalyzerError, DataProcessingError, MissingColumnError, 
    InvalidFileFormatError, EmptyDataError, error_handler
)
from url_analyzer.utils.logging import get_logger
from url_analyzer.utils.memory_pool import string_pool, MemoryTracker, get_memory_usage

# Create a logger for this module
logger = get_logger(__name__)

# Default chunk size (number of rows)
DEFAULT_CHUNK_SIZE = 10000

def read_file_in_chunks(
    file_path: str, 
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> Generator[pd.DataFrame, None, None]:
    """
    Read a file in chunks to reduce memory usage.
    
    Args:
        file_path: Path to the file to read
        chunk_size: Number of rows to read in each chunk
        
    Yields:
        DataFrame chunks
        
    Raises:
        InvalidFileFormatError: If the file format is invalid or cannot be parsed
        DataProcessingError: If there's an error reading the file
    """
    logger.info(f"Reading file in chunks: {os.path.basename(file_path)} (chunk size: {chunk_size})")
    
    # Validate file exists
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    try:
        if file_path.lower().endswith('.csv'):
            # For CSV files, use the built-in chunking in pandas
            chunks = pd.read_csv(file_path, chunksize=chunk_size, on_bad_lines='skip')
            for i, chunk in enumerate(chunks):
                if chunk.empty:
                    logger.warning(f"Empty chunk encountered (chunk {i+1})")
                    continue
                
                # Clean column names
                chunk.columns = [re.sub(r'[^a-zA-Z0-9_]', '', col.replace(' ', '_')) for col in chunk.columns]
                logger.debug(f"Processed chunk {i+1} with {len(chunk)} rows")
                yield chunk
                
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            # Excel files need to be read differently since pandas doesn't support chunking for Excel
            # We'll read the file in one go but process it in chunks
            logger.warning("Excel files are read entirely into memory before chunking")
            df = pd.read_excel(file_path)
            
            if df.empty:
                error_msg = f"File is empty: {os.path.basename(file_path)}"
                logger.error(error_msg)
                raise EmptyDataError(error_msg)
            
            # Clean column names
            df.columns = [re.sub(r'[^a-zA-Z0-9_]', '', col.replace(' ', '_')) for col in df.columns]
            
            # Process in chunks
            total_rows = len(df)
            for i in range(0, total_rows, chunk_size):
                chunk = df.iloc[i:min(i+chunk_size, total_rows)]
                logger.debug(f"Processed chunk {i//chunk_size+1} with {len(chunk)} rows")
                yield chunk
        else:
            error_msg = f"Unsupported file format: {os.path.splitext(file_path)[1]}"
            logger.error(error_msg)
            raise InvalidFileFormatError(error_msg)
            
    except pd.errors.ParserError as e:
        error_msg = f"Error parsing file {os.path.basename(file_path)}: {e}"
        logger.error(error_msg)
        raise InvalidFileFormatError(error_msg, {"original_error": str(e)})
    except Exception as e:
        error_msg = f"Error reading file {os.path.basename(file_path)}: {e}"
        logger.error(error_msg)
        raise DataProcessingError(error_msg, {"original_error": str(e)})


def process_chunk(
    chunk: pd.DataFrame, 
    url_column: str,
    compiled_patterns: Dict[str, Any],
    chunk_index: int = 0
) -> pd.DataFrame:
    """
    Process a single chunk of data.
    
    Args:
        chunk: DataFrame chunk to process
        url_column: Name of the URL column
        compiled_patterns: Dictionary of compiled regex patterns
        chunk_index: Index of the current chunk (for logging)
        
    Returns:
        Processed DataFrame chunk
        
    Raises:
        DataProcessingError: If there's an error processing the chunk
        MissingColumnError: If a required column is missing
    """
    logger.debug(f"Processing chunk {chunk_index+1} with {len(chunk)} rows")
    
    # Check for required columns
    if url_column not in chunk.columns:
        error_msg = f"Required column '{url_column}' not found in chunk {chunk_index+1}"
        logger.error(error_msg)
        raise MissingColumnError(error_msg, {"column": url_column})
    
    try:
        # Use vectorized operations where possible
        # For URL classification, we still need to use apply since it's a complex operation
        if TQDM_AVAILABLE:
            tqdm.pandas(desc=f"Classifying URLs (chunk {chunk_index+1})")
            results = chunk[url_column].progress_apply(lambda url: classify_url(url, compiled_patterns))
        else:
            results = chunk[url_column].apply(lambda url: classify_url(url, compiled_patterns))
        
        # Extract results into separate columns
        chunk['URL_Category'] = [res[0] for res in results]
        chunk['Is_Sensitive'] = [res[1] for res in results]
        
        # Extract base domains
        if TQDM_AVAILABLE:
            tqdm.pandas(desc=f"Extracting Base Domains (chunk {chunk_index+1})")
            chunk['Base_Domain'] = chunk[url_column].progress_apply(get_base_domain)
        else:
            chunk['Base_Domain'] = chunk[url_column].apply(get_base_domain)
        
        # Initialize Notes column
        chunk['Notes'] = ''
        
        return chunk
    except Exception as e:
        error_msg = f"Error processing chunk {chunk_index+1}: {e}"
        logger.error(error_msg)
        raise DataProcessingError(error_msg, {"original_error": str(e)})


def process_file_in_chunks(
    file_path: str, 
    compiled_patterns: Dict[str, Any], 
    cli_args: Any,
    chunk_size: int = DEFAULT_CHUNK_SIZE
) -> pd.DataFrame:
    """
    Process a file in chunks to improve memory efficiency.
    
    Args:
        file_path: Path to the file to process
        compiled_patterns: Dictionary of compiled regex patterns
        cli_args: Command-line arguments
        chunk_size: Number of rows to process in each chunk
        
    Returns:
        Processed DataFrame
        
    Raises:
        InvalidFileFormatError: If the file format is invalid or cannot be parsed
        MissingColumnError: If a required column is missing
        DataProcessingError: If there's an error processing the data
        EmptyDataError: If the file is empty or no valid data is found
    """
    logger.info(f"Processing file in chunks: {os.path.basename(file_path)}")
    print(f"\n--- Processing: {os.path.basename(file_path)} (chunked mode) ---")
    
    # URL column name
    url_column = 'Domain_name'
    
    # Process the file in chunks
    processed_chunks = []
    chunk_count = 0
    
    try:
        # Create a generator for reading chunks
        chunks_generator = read_file_in_chunks(file_path, chunk_size)
        
        # Process each chunk
        for i, chunk in enumerate(chunks_generator):
            chunk_count += 1
            processed_chunk = process_chunk(chunk, url_column, compiled_patterns, i)
            processed_chunks.append(processed_chunk)
            
            # Log progress
            logger.info(f"Processed chunk {i+1} with {len(chunk)} rows")
            if i % 10 == 0 and i > 0:  # Log memory usage every 10 chunks
                import psutil
                process = psutil.Process(os.getpid())
                memory_usage = process.memory_info().rss / 1024 / 1024  # in MB
                logger.info(f"Memory usage after {i+1} chunks: {memory_usage:.2f} MB")
        
        # Combine all processed chunks
        if not processed_chunks:
            error_msg = f"No valid data found in {os.path.basename(file_path)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            raise EmptyDataError(error_msg)
        
        logger.info(f"Combining {len(processed_chunks)} processed chunks")
        df = pd.concat(processed_chunks, ignore_index=True)
        
        # Perform live scan if requested
        if cli_args.live_scan:
            try:
                uncategorized_urls = df[df['URL_Category'] == 'Uncategorized'][url_column].dropna().unique().tolist()
                if uncategorized_urls:
                    logger.info(f"Performing live scan on {len(uncategorized_urls)} URLs")
                    print(f"⚡ Performing live scan on {len(uncategorized_urls)} unique uncategorized URLs...")
                    
                    # Get configuration
                    from url_analyzer.config.manager import load_config
                    from url_analyzer.utils.concurrency import create_thread_pool_executor
                    config = load_config()
                    
                    # Create thread pool executor with adaptive settings
                    # Use "io" operation type since URL scanning is I/O-bound
                    # The executor will automatically optimize the number of workers
                    with create_thread_pool_executor(config, operation_type="io") as executor:
                        future_map = {
                            executor.submit(fetch_url_data, url, cli_args.summarize, config): url 
                            for url in uncategorized_urls
                        }
                        
                        # Track progress if tqdm is available
                        if TQDM_AVAILABLE:
                            for future in tqdm(concurrent.futures.as_completed(future_map), 
                                              total=len(uncategorized_urls),
                                              desc="Live Scanning"):
                                try:
                                    _, scan_result = future.result()
                                    LIVE_SCAN_CACHE[future_map[future]] = scan_result
                                except Exception as e:
                                    logger.warning(f"Error scanning URL {future_map[future]}: {e}")
                                    # Continue with other URLs even if one fails
                        else:
                            print("Scanning URLs...")
                            for future in concurrent.futures.as_completed(future_map):
                                try:
                                    _, scan_result = future.result()
                                    LIVE_SCAN_CACHE[future_map[future]] = scan_result
                                except Exception as e:
                                    logger.warning(f"Error scanning URL {future_map[future]}: {e}")
                                    # Continue with other URLs even if one fails

                    # Add scan results to Notes column
                    def get_note(row):
                        if row['URL_Category'] == 'Uncategorized':
                            data = LIVE_SCAN_CACHE.get(row[url_column], {})
                            title = data.get('title', '')
                            summary = data.get('summary', '')
                            return f"Title: {title}" + (f" | Summary: {summary}" if summary else "")
                        return ''

                    # Process Notes in chunks to avoid memory issues with large DataFrames
                    chunk_size = 50000
                    total_rows = len(df)
                    
                    if TQDM_AVAILABLE:
                        with tqdm(total=total_rows, desc="Adding Notes") as pbar:
                            for i in range(0, total_rows, chunk_size):
                                end_idx = min(i + chunk_size, total_rows)
                                df.loc[i:end_idx-1, 'Notes'] = df.iloc[i:end_idx].apply(get_note, axis=1)
                                pbar.update(end_idx - i)
                    else:
                        print("Adding Notes...")
                        for i in range(0, total_rows, chunk_size):
                            end_idx = min(i + chunk_size, total_rows)
                            df.loc[i:end_idx-1, 'Notes'] = df.iloc[i:end_idx].apply(get_note, axis=1)
            except Exception as e:
                # Log the error but don't fail the entire process
                error_msg = f"Error during live scan in {os.path.basename(file_path)}: {e}"
                logger.error(error_msg)
                print(f"⚠️ {error_msg}")
                # Continue processing without live scan results
        
        logger.info(f"Successfully processed file in chunks: {os.path.basename(file_path)}")
        print(f"✅ Processed {chunk_count} chunks with a total of {len(df)} rows")
        return df
        
    except Exception as e:
        error_msg = f"Error processing file in chunks: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        raise