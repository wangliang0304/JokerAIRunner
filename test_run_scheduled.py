"""
Test script to demonstrate the usage of run_scheduled function.
"""
import logging

from run_scheduled import run_scheduled

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    # Example 1: Run all tests using run_main
    # run_scheduled("Daily scheduled job")

    # Example 2: Run specific test paths
    run_scheduled(
        "Custom scheduled job",
        test_paths=["testcases/pp_app/data/data_network_query_test.py"],
        run_report=True,
        upload_report_flag=False  # Set to False to avoid uploading during testing
    )

    # Example 3: Run multiple test paths without generating report
    # run_scheduled(
    #     "Multiple paths job",
    #     test_paths=["testcases/pp_app/data", "testcases/Bussiness/data"],
    #     run_report=False,
    #     upload_report_flag=False
    # )
