import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def job(output_dir="output/"):
    """The actual work that runs on schedule."""
    from src.reporter import generate_report
    from src.db import get_data  # read-only connection, see P2 below

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}report_{timestamp}.pdf"

    try:
        data = get_data()
        generate_report(data, [], filename)
        logger.info(f"[{timestamp}] Report generated: {filename}")
    except Exception as e:
        logger.error(f"[{timestamp}] Report generation failed: {e}")


def schedule_report(hour=8, minute=0, output_dir="output/"):
    """Registers the daily cron job. Call once at app startup."""
    scheduler.add_job(
        job,
        "cron",
        hour=hour,
        minute=minute,
        kwargs={"output_dir": output_dir},
        id="daily_report",
        replace_existing=True,  # avoids duplicate jobs if called twice
    )
    if not scheduler.running:
        scheduler.start()
    logger.info(f"Scheduled daily report at {hour:02d}:{minute:02d}")


def get_next_run_time():
    """Used by the settings panel (P3) to display next run time."""
    job_ref = scheduler.get_job("daily_report")
    return job_ref.next_run_time if job_ref else None