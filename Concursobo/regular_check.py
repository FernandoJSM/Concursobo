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

    def job_smv2022():
        telegram_bot.auto_check(scraper_name="SMV 2022")

    def job_fundep():
        telegram_bot.auto_check(scraper_name="Fundep")

    def job_corridasbr():
        telegram_bot.auto_check(scraper_name="CorridasBR")

    def job_pci():
        telegram_bot.auto_check(scraper_name="PCI Concursos")

    scheduler.add_job(
        func=job_cem2021,
        trigger="cron",
        day_of_week="0-4",
        hour="7,11,15,17",
        minute="0",
    )
    scheduler.add_job(
        func=job_smv2022,
        trigger="cron",
        day_of_week="0-4",
        hour="7,11,15,17",
        minute="1",
    )
    scheduler.add_job(
        func=job_corridasbr,
        trigger="cron",
        day_of_week="0-4",
        hour="8,17",
        minute="2"
    )
    scheduler.add_job(
        func=job_fundep,
        trigger="cron",
        day_of_week="0-4",
        hour="8,17",
        minute="3"
    )
    scheduler.add_job(
        func=job_pci,
        trigger="cron",
        day_of_week="0-4",
        hour="8,17",
        minute="4"
    )

    scheduler.start()

    while True:
        time.sleep(100)
