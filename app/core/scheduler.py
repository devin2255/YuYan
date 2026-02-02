from apscheduler.schedulers.background import BackgroundScheduler

from yuyan.app.services.cache import update_cache_data


def create_scheduler(ctx) -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: update_cache_data(ctx),
        trigger="interval",
        minutes=5,
        id="updateCache",
        replace_existing=True,
    )
    return scheduler
