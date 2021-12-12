import json
import logging
import os
import re
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup

from Concursobo.scrapers.base_scraper import BaseScraper
from Concursobo import utils
from Concursobo.constants import AcquisitionStatus


class MarinhaSMVScraper(BaseScraper):
    """
        Extrai os dados da página do concurso SMV do 1o distrito da Marinha do Brasil
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
        self.url = "https://www.marinha.mil.br/com1dn/smv/smv-sup-areas-av-conv"

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(message)s",
            level=logging.INFO,
            datefmt="%d-%m-%Y %H:%M:%S",
        )

        self.logger = logging.getLogger(name=name)

    def scrape_page(self):
        """
            Coleta os dados da página do concurso da Marinha
        Returns:
            (AcquisitionStatus): Indica o status da aquisição, se houve sucesso e / ou atualização dos dados
        """
        self.logger.info(msg="Acessando a página...")
        webpage = requests.get(url=self.url)

        if webpage.status_code != 200:
            self.logger.info(msg="Não foi possível acessar a página")
            return AcquisitionStatus.ERROR

        self.logger.info(msg="Página acessada, obtendo os dados...")

        soup = BeautifulSoup(markup=webpage.text, features="html.parser")

        # Título da página
        title = soup.find_all(name="h1", class_="page-header")[0].text

        # Tabela das informações
        tables_soup = soup.findAll(name="table", class_="views-table cols-0 table table-hover table-striped")

        message_list = list()

        for table_soup in tables_soup:
            rows_soup = table_soup.findAll(name="tr")

            for row_soup in rows_soup:
                row_data = row_soup.findAll(name="td")
                date = re.sub(pattern=r"[\n\t\xa0]", repl="", string=row_data[0].text)
                message = re.sub(pattern=r"[\n\t\xa0]", repl="", string=row_data[1].text)
                url = row_data[2].findAll(name="a")[0].attrs["href"]
                msg_data = {
                    "date": date.strip(),
                    "message": message.strip(),
                    "url": url,
                }
                message_list.append(msg_data)

        self.logger.info(msg=f"{len(message_list)} mensagens capturadas")

        timezone = pytz.timezone(
            zone=utils.get_config().get(section="timezone", option="PYTZ_TIMEZONE")
        )
        current_time = datetime.now(tz=timezone)

        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_data = {
            "title": title,
            "url": self.url,
            "acquisition_date": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "messages": message_list,
            "last_update": stored_data["last_update"],
            "last_update_date": stored_data["last_update_date"],
        }

        self.logger.info(
            msg="Comparando com a aquisição do dia "
            + stored_data["acquisition_date"]
            + "..."
        )

        updated_messages, _ = utils.list_difference(
            list_A=message_list, list_B=stored_data["messages"]
        )

        if len(updated_messages) == 0:
            self.logger.info(msg="Nenhuma alteração encontrada")

            with open(file=self.db_path, mode="w") as f:
                json.dump(output_data, f, indent=4)

            return AcquisitionStatus.UNCHANGED

        self.logger.info(msg=f"{len(updated_messages)} alterações encontradas!")

        output_data["last_update"] = updated_messages
        output_data["last_update_date"] = current_time.strftime("%d/%m/%Y %H:%M:%S")

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
            info_str = info["date"] + " - "
            info_str += "<a href=\"" + info["url"] + "\">" + info["message"] + "</a>"
            info_str += bar_str

            output_message_list.append(info_str)

        return output_message_list

    def updated_data(self):
        """
            Retorna os dados que foram atualizados
        Returns:
            output_message_list (list of str): Lista com as mensagens de saída
        """
        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message_list = list()

        if len(stored_data["last_update"]) == 1:
            output_message_list.append(
                (
                        str(len(stored_data["last_update"]))
                        + " atualização obtida para:\n"
                )
            )
        else:
            output_message_list.append(
                (
                        str(len(stored_data["last_update"]))
                        + " atualizações obtidas para:\n"
                )
            )

        output_message_list.append(
            "<a href=\"" + stored_data["url"] + "\">" + stored_data["title"] + "</a>"
        )
        output_message_list.extend(
            self.generate_message(message_list=stored_data["last_update"])
        )

        output_message_list = utils.group_messages(message_list=output_message_list)

        return output_message_list

    def short_data(self):
        """
            Retorna os dados da página de forma resumida
        Returns:
            output_message_list (list of str): Lista com as mensagens de saída
        """

        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message_list = [
            ("<a href=\"" + stored_data["url"] + "\">" + stored_data["title"] + "</a>")
        ]
        output_message_list.extend(
            self.generate_message(message_list=stored_data["messages"][0:3])
        )
        output_message_list.append(
            "\n<b>Dados salvos no dia " + stored_data["acquisition_date"] + "</b>"
        )

        output_message_list = utils.group_messages(message_list=output_message_list)

        return output_message_list

    def complete_data(self):
        """
            Retorna todos os dados salvos da página
        Returns:
            output_message_list (list of str): Lista com as mensagens de saída
        """
        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message_list = [
            ("<a href=\"" + stored_data["url"] + "\">" + stored_data["title"] + "</a>")
        ]
        output_message_list.extend(
            self.generate_message(message_list=stored_data["messages"])
        )
        output_message_list.append(
            "\n<b>Dados salvos no dia " + stored_data["acquisition_date"] + "</b>"
        )

        output_message_list = utils.group_messages(message_list=output_message_list)

        return output_message_list

    def __repr__(self):
        return (
            f"Scraper {self.name}: "
            f"\n URL: {self.url}"
            f"\n Database_path: {self.db_path}"
        )


if __name__ == "__main__":
    """
    Rotina de teste do scraper, acessa a página, salva o arquivo e executa as
    funções da classe base
    """

    database_path = os.path.join(utils.get_data_path(), "smv2022.json")
    smv2022 = MarinhaSMVScraper(name="SMV 2022", database_path=database_path)

    status = smv2022.scrape_page()

    if status:
        print("\n\nMensagem de atualização:")
        print(smv2022.updated_data())
        print("\n\nMensagem de resumo:")
        print(smv2022.short_data())
        print("\n\nMensagem completa: ")
        print(smv2022.complete_data())
    else:
        print("Erro no acesso à página")
