import os
import sys

# Necessário para a execução pelo pm2
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time

from Concursobo import utils
from Concursobo.concursobo import build_bot


from apscheduler.schedulers.background import BackgroundScheduler

if __name__ == "__main__":
    """
    Runs the pool and send method and send messages only if there is an update
    """
    telegram_bot = build_bot()
    scheduler = BackgroundScheduler()

    timezone = utils.get_config().get(section="timezone", option="PYTZ_TIMEZONE")
    scheduler.configure(timezone=timezone)

    def job_cem2021():
        telegram_bot.auto_check(scraper_name="CP-CEM 2021")

    def job_fundep():
        telegram_bot.auto_check(scraper_name="Fundep")

    scheduler.add_job(
        func=job_cem2021,
        trigger="cron",
        day_of_week="1-5",
        hour="8,12,16,18",
        minute="0",
    )
    scheduler.add_job(
        func=job_fundep, trigger="cron", day_of_week="1-5", hour="9,16,18", minute="0"
    )

    scheduler.start()

    while True:
        time.sleep(100)
