import os
import sys
import tempfile
import pandas as pd

# Create a temporary CSV file with test data
def create_test_csv():
    temp_file = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    temp_filename = temp_file.name
    
    # Create a simple DataFrame with test data
    data = {
        'Domain_name': [
            'google.com',
            'facebook.com',
            'example.com/user/123',
            'analytics.google.com',
            'doubleclick.net'
        ],
        'Access_time': [
            '2025-08-04 10:00:00',
            '2025-08-04 11:30:00',
            '2025-08-04 12:45:00',
            '2025-08-04 14:15:00',
            '2025-08-04 16:00:00'
        ]
    }
    
    df = pd.DataFrame(data)
    df.to_csv(temp_filename, index=False)
    temp_file.close()
    
    return temp_filename

# Test the report generation
def test_report_generation():
    print("Creating test CSV file...")
    test_file = create_test_csv()
    print(f"Test file created at: {test_file}")
    
    # Import the main script
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the script with the test file
    print("\nRunning URL analyzer with --live-scan and --summarize options...")
    cmd = f'python -m url_analyzer analyze --path "{test_file}" --live-scan --summarize'
    print(f"Command: {cmd}")
    
    # Execute the command
    exit_code = os.system(cmd)
    
    # Check the result
    if exit_code == 0:
        print("\n✅ Test passed: The script executed successfully.")
    else:
        print(f"\n❌ Test failed: The script exited with code {exit_code}.")
    
    # Clean up
    try:
        os.unlink(test_file)
        print(f"Test file deleted: {test_file}")
    except:
        print(f"Could not delete test file: {test_file}")

if __name__ == "__main__":
    test_report_generation()