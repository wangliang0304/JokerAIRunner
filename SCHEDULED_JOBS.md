# Scheduled Jobs Documentation

This document explains how to use the `run_scheduled` function for running automated tests as scheduled jobs.

## Overview

The `run_scheduled` function in `run_scheduled.py` allows you to run automated tests with customized execution options.
It can be used to:

1. Run all tests using the standard `run_main` function
2. Run specific test paths with custom options
3. Control whether to generate Allure reports
4. Control whether to upload reports to the server

## Function Signature

```python
def run_scheduled(scheduled_job, test_paths=None, run_report=True, upload_report_flag=True):
    """
    Run scheduled job with customized execution options.
    
    Args:
        scheduled_job: The scheduled job information
        test_paths: Optional list of test paths to run. If None, runs all tests using run_main
        run_report: Whether to generate Allure report
        upload_report_flag: Whether to upload the report to server
    """
```

## Usage Examples

### Example 1: Run All Tests

To run all tests using the standard `run_main` function:

```python
from run_scheduled import run_scheduled

# Run all tests
run_scheduled("Daily scheduled job")
```

### Example 2: Run Specific Test Paths

To run specific test paths:

```python
from run_scheduled import run_scheduled

# Run a specific test file
run_scheduled(
    "Custom scheduled job",
    test_paths=["testcases/pp_app/data/data_network_query_test.py"],
    run_report=True,
    upload_report_flag=True
)
```

### Example 3: Run Multiple Test Paths

To run multiple test paths:

```python
from run_scheduled import run_scheduled

# Run multiple test directories
run_scheduled(
    "Multiple paths job",
    test_paths=["testcases/pp_app/data", "testcases/Bussiness/data"],
    run_report=True,
    upload_report_flag=True
)
```

### Example 4: Run Tests Without Generating Reports

To run tests without generating Allure reports:

```python
from run_scheduled import run_scheduled

# Run tests without generating reports
run_scheduled(
    "No report job",
    test_paths=["testcases/pp_app/data"],
    run_report=False,
    upload_report_flag=False
)
```

## Integration with Scheduling Systems

The `run_scheduled` function can be integrated with various scheduling systems:

### Using Windows Task Scheduler

1. Create a batch file (e.g., `run_scheduled_job.bat`) with the following content:
   ```batch
   cd /d D:\path\to\your\project
   python -c "from run_scheduled import run_scheduled; run_scheduled('Daily job', test_paths=['testcases/palmpay/data'])"
   ```

2. Set up a scheduled task in Windows Task Scheduler to run this batch file at your desired schedule.

### Using Cron (Linux/macOS)

1. Create a shell script (e.g., `run_scheduled_job.sh`) with the following content:
   ```bash
   #!/bin/bash
   cd /path/to/your/project
   python -c "from run_scheduled import run_scheduled; run_scheduled('Daily job', test_paths=['testcases/palmpay/data'])"
   ```

2. Make the script executable:
   ```bash
   chmod +x run_scheduled_job.sh
   ```

3. Add a cron job to run this script at your desired schedule:
   ```
   0 0 * * * /path/to/your/project/run_scheduled_job.sh
   ```

### Using Python's schedule Library

You can also use Python's `schedule` library to run scheduled jobs:

```python
import schedule
import time
from run_scheduled import run_scheduled


def job():
    run_scheduled("Daily job", test_paths=["testcases/pp_app/data"])


# Schedule job to run at 2:00 AM every day
schedule.every().day.at("02:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

## Logging

The `run_scheduled` function includes logging to help track the execution of scheduled jobs. Make sure to configure
logging in your application:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="scheduled_jobs.log"  # Optional: log to file
)
```
