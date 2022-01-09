import os
import sys

# Necessário para a execução pelo pm2
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Concursobo.concursobo import build_bot

if __name__ == "__main__":
    """
    Runs the pool and send method and send messages only if there is an update
    """
    telegram_bot = build_bot()

    telegram_bot.auto_check(scraper_name="CP-CEM 2021")
    telegram_bot.auto_check(scraper_name="SMV 2022")
    telegram_bot.auto_check(scraper_name="Fundep")
    telegram_bot.auto_check(scraper_name="CorridasBR")
    telegram_bot.auto_check(scraper_name="PCI Concursos")
