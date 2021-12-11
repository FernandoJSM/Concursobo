import os
import sys

# Necessário para a execução pelo pm2
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Concursobo import utils
from Concursobo.scrapers.fundep_scraper import FundepScraper
from Concursobo.scrapers.marinha_scraper import MarinhaScraper
from Concursobo.scrapers.pci_scraper import PCIScraper
from Concursobo.telegram_bot import TelegramBot


def build_bot():
    """
        Constrói a base do bot com todos os scrapers cadastrados
    Returns:
        telegram_bot (TelegramBot): Classe do bot
    """
    token = utils.get_config().get(section="telegram", option="BOT_TOKEN")
    contacts_path = os.path.join(utils.get_data_path(), "contacts_list.json")

    scraper_list = [
        MarinhaScraper(
            name="CP-CEM 2021",
            database_path=os.path.join(utils.get_data_path(), "cem2021.json"),
            url="https://www.inscricao.marinha.mil.br/marinha/index_concursos.jsp?id_concurso=401",
        ),
        FundepScraper(
            name="Fundep",
            database_path=os.path.join(utils.get_data_path(), "fundep.json"),
        ),
        PCIScraper(
            name="PCI Concursos",
            database_path=os.path.join(utils.get_data_path(), "pci.json"),
            store_size=7,
            keywords=[
                "automacao",
                "eletrica",
                "eletricidade",
                "eletronica analogica",
                "eletronica digital",
                "eletrotecnica",
                "engenharia elet",
                "engenheiro elet",
                "marinha",
                "telecom",
            ],
            ignore_words=["estagio", "estagiario", "aprendiz", "suspens"],
        ),
    ]

    telegram_bot = TelegramBot(
        token=token, scraper_list=scraper_list, contacts_path=contacts_path
    )

    return telegram_bot


if __name__ == "__main__":
    """
    Cadastro dos scrapers, envio de uma mensagem e execução do bot para recepção de comandos
    """
    telegram_bot = build_bot()
    telegram_bot.start_pooling()
