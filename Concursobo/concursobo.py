import os
import sys

# Necessário para a execução pelo pm2
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from Concursobo import utils
from Concursobo.scrapers.marinha_scraper import MarinhaScraper
from Concursobo.scrapers.marinha_smv_scraper import MarinhaSMVScraper
from Concursobo.scrapers.fundep_scraper import FundepScraper
from Concursobo.scrapers.corridasbr_scraper import CorridasBRScraper
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
        MarinhaSMVScraper(
            name="SMV 2022",
            database_path=os.path.join(utils.get_data_path(), "smv2022.json"),
        ),
        FundepScraper(
            name="Fundep",
            database_path=os.path.join(utils.get_data_path(), "fundep.json"),
        ),
        CorridasBRScraper(
            name="CorridasBR",
            database_path=os.path.join(utils.get_data_path(), "corridasbr.json"),
            base_url="http://www.corridasbr.com.br/MG/",
            table_url="http://www.corridasbr.com.br/MG/por_regiao.asp?regi%E3o=Metropolitana%20de%20Belo%20Horizonte",
            max_distance=5,
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
