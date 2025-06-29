"""
Example of using the schedule library to run scheduled jobs.
Install the schedule library with: pip install schedule
"""
import schedule
import time
import logging

from run_scheduled import run_scheduled

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def daily_job():
    """Run all tests daily"""
    logging.info("开始执行定时任务 daily_job .")

    run_scheduled("Daily full test run")


def weekly_job():
    """Run specific tests weekly"""
    run_scheduled(
        "Weekly specific test run",
        test_paths=["testcases/pp_app/data", "testcases/Bussiness/data"],
        run_report=True,
        upload_report_flag=True
    )


def hourly_job():
    """Run quick tests hourly"""
    run_scheduled(
        "Hourly quick test",
        run_report=True,
        upload_report_flag=True
    )


if __name__ == "__main__":
    # Schedule jobs
    schedule.every().day.at("07:00").do(daily_job)  # Run daily at 1:00 AM
    # schedule.every().monday.at("03:00").do(weekly_job)  # Run weekly on Monday at 3:00 AM
    # schedule.every().hour.do(hourly_job)  # Run hourly

    # 几分钟之后运行一次
    # schedule.every(1).minutes.do(hourly_job)
    # 立即执行
    # hourly_job()

    logging.info("Scheduler started. Press Ctrl+C to exit.")

    # Keep the script running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logging.info("Scheduler stopped.")