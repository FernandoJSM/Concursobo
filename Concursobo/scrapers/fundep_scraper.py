import json
import logging
import os
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup

from Concursobo import utils
from Concursobo.constants import AcquisitionStatus
from Concursobo.scrapers.base_scraper import BaseScraper


class FundepScraper(BaseScraper):
    """
    Extrai os dados da página de vagas da FUNDEP
    """

    def __init__(self, name, database_path):
        """
            Inicializa a classe
        Args:
            name (str): Nome do scraper
            database_path (str): Caminho para o arquivo onde estão salvos os dados
        """

        self.name = name
        self.db_path = database_path
        self.url = "https://www.fundep.ufmg.br/vagas/vagas-projetos/"

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(message)s",
            level=logging.INFO,
            datefmt="%d-%m-%Y %H:%M:%S",
        )

        self.logger = logging.getLogger(name=name)

    def scrape_page(self):
        """
        Coleta os dados da página da Fundep
        """
        self.logger.info(msg="Acessando a página...")
        webpage = requests.get(url=self.url)

        if webpage.status_code != 200:
            self.logger.info(msg="Não foi possível acessar a página")
            return AcquisitionStatus.ERROR

        self.logger.info(msg="Página acessada, obtendo os dados...")

        soup = BeautifulSoup(markup=webpage.text, features="html.parser")

        jobs_info = soup.find_all("li", {"class": "column column-block"})

        all_jobs = list()

        for job in jobs_info:
            job_title = job.text.split("\n")[1]
            job_description = ""
            for p in job.find_all("p"):
                job_description += p.text
            job_url = None
            for url in job.find_all("a"):
                if "Mais informações" in url.text:
                    job_url = url["href"]

            job_data = {
                "title": job_title,
                "description": job_description,
                "url": job_url,
            }
            all_jobs.append(job_data)

        self.logger.info(msg=f"{len(all_jobs)} vagas capturadas")

        timezone = pytz.timezone(
            zone=utils.get_config().get(section="timezone", option="PYTZ_TIMEZONE")
        )
        current_time = datetime.now(tz=timezone)

        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_data = {
            "url": self.url,
            "acquisition_date": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "all_jobs": all_jobs,
            "last_update": stored_data["last_update"],
        }

        self.logger.info(
            msg="Comparando com a aquisição do dia "
            + stored_data["acquisition_date"]
            + "..."
        )

        update_added, update_removed = utils.list_difference(
            list_A=all_jobs, list_B=stored_data["all_jobs"]
        )

        if len(update_added) == 0 and len(update_removed) == 0:
            self.logger.info(msg="Nenhuma alteração encontrada")

            with open(file=self.db_path, mode="w") as f:
                json.dump(output_data, f, indent=4)

            return AcquisitionStatus.UNCHANGED

        if update_added:
            self.logger.info(msg=f"{len(update_added)} vagas adicionadas!")

        if update_added:
            self.logger.info(msg=f"{len(update_removed)} vagas removidas!")

        last_update = {
            "date": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "jobs_added": update_added,
            "jobs_removed": update_removed,
        }

        output_data["last_update"] = last_update

        with open(file=self.db_path, mode="w") as f:
            json.dump(output_data, f, indent=4)

        return AcquisitionStatus.UPDATED

    @staticmethod
    def generate_message(message_list):
        """
            Gera mensagens a partir de uma lista
        Args:
            message_list (list of dict): Lista com os dicionários de mensagens deste scraper

        Returns:
            output_message_list (list of str): Lista com as mensagens de saída
        """
        bar_str = "\n-------------------------------\n"

        output_message_list = [bar_str]

        for info in message_list:
            info_str = "<a href=\"" + info["url"] + "\">" + info["title"] + "</a>"
            info_str += bar_str

            output_message_list.append(info_str)

        return output_message_list

    def updated_data(self):
        """
            Retorna os dados que foram atualizados
        Returns:
            output_message_list (list of str): Lista com a mensagem de saída
        """
        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message_list = [
            "<a href=\"" + stored_data["url"] + "\">" + self.name + ":</a>"
        ]

        if stored_data["last_update"]["jobs_added"]:
            output_message_list.append(
                "\n"
                + str(len(stored_data["last_update"]["jobs_added"]))
                + " vaga(s) adicionada(s):"
            )
            output_message_list.extend(
                self.generate_message(
                    message_list=stored_data["last_update"]["jobs_added"]
                )
            )

        if stored_data["last_update"]["jobs_removed"]:
            output_message_list.append(
                "\n\n"
                + str(len(stored_data["last_update"]["jobs_removed"]))
                + " vaga(s) removida(s):"
            )
            output_message_list.extend(
                self.generate_message(
                    message_list=stored_data["last_update"]["jobs_removed"]
                )
            )

        output_message_list = utils.group_messages(message_list=output_message_list)

        return output_message_list

    def short_data(self):
        """
            Retorna os dados da página de forma resumida
        Returns:
            output_message_list (list of str): Lista com a mensagem de saída
        """
        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message_list = [
            (
                "<a href=\""
                + stored_data["url"]
                + "\">Últimas vagas adicionadas em"
                + self.name
                + ":</a>"
            )
        ]
        bar_str = "\n-------------------------------\n"

        if stored_data["last_update"]["jobs_added"]:
            for info in stored_data["last_update"]["jobs_added"]:
                info_str = "<a href=\"" + info["url"] + "\">" + info["title"] + "</a>"
                info_str += "\n" + info["description"]
                info_str += bar_str

                output_message_list.append(info_str)

        output_message_list = utils.group_messages(message_list=output_message_list)

        return output_message_list

    def complete_data(self):
        """
           Retorna todos os dados salvos da página
        Returns:
            output_message_list (list of str): Lista com a mensagem de saída
        """
        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message_list = [
            (
                "<a href=\""
                + stored_data["url"]
                + "\">Vagas disponíves em "
                + self.name
                + "</a>"
            )
        ]

        output_message_list.extend(
            self.generate_message(message_list=stored_data["all_jobs"])
        )
        output_message_list.append(
            "<b>Dados salvos no dia " + stored_data["acquisition_date"] + "</b>"
        )

        output_message_list = utils.group_messages(message_list=output_message_list)

        return output_message_list


if __name__ == "__main__":
    """
    Rotina de teste do scraper, acessa a página, salva o arquivo e executa as
    funções da classe base
    """

    database_path = os.path.join(utils.get_data_path(), "fundep.json")
    fundep = FundepScraper(name="Fundep", database_path=database_path)

    status = fundep.scrape_page()

    if status:
        print("\n\nMensagem de atualização:")
        print(fundep.updated_data())
        print("\n\nMensagem de resumo:")
        print(fundep.short_data())
        print("\n\nMensagem completa: ")
        print(fundep.complete_data())
    else:
        print("Erro no acesso à página")
