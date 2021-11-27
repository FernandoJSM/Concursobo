import json
import logging
import os
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup

from Concursobo.scrapers.base_scraper import BaseScraper
from Concursobo import utils
from Concursobo.constants import AcquisitionStatus


class MarinhaScraper(BaseScraper):
    """
        Extrai os dados da página de concursos geral da Marinha do Brasil
    """

    def __init__(self, name, database_path, url):
        """
            Inicializa a classe
        Args:
            name (str): Nome do scraper
            database_path (str): Caminho para o arquivo onde estão salvos os dados
            url (str): URL da página do concurso da Marinha do Brasil no formato
                https://www.inscricao.marinha.mil.br/marinha/index_concursos.jsp?id_concurso=000
        """

        self.name = name
        self.db_path = database_path
        self.url = url

        logging.basicConfig(format="%(asctime)s - %(name)s - %(message)s", level=logging.INFO,
                            datefmt="%d-%m-%Y %H:%M:%S")

        self.logger = logging.getLogger(name=name)

    def scrape_page(self):
        """
            Coleta os dados da página do concurso
        Returns:
            (AcquisitionStatus): Indica o status da aquisição, se houve sucesso e / ou atualização dos dados
        """
        self.logger.info(msg="Acessando a página...")
        webpage = requests.get(url=self.url)

        if webpage.status_code != 200:
            self.logger.info(msg="Não foi possível acessar a página")
            return AcquisitionStatus.ERROR

        self.logger.info(msg="Página acessada, obtendo os dados...")

        soup = BeautifulSoup(markup=webpage.text, features='html.parser')

        # Título da página
        title = soup.find_all(name="span", class_="header0")[0].text

        # Data do concurso
        raw_date_text = webpage.text.split("Data da Prova")[1]
        split_s = raw_date_text.find("<table")
        split_e = raw_date_text.find("</table")
        date_text = raw_date_text[split_s:split_e]
        date_soup = BeautifulSoup(markup=date_text + "</table>", features='html.parser')

        exam_date = date_soup.text.replace('\n', '').replace('\t', '').replace('\r', '')

        # Tabela das informações
        info_table_config = {
            'height': '24',
            'width': '46',
            'align': 'right',
            'valign': 'middle',
        }

        info_table_soup = soup.findAll(name='td', attrs=info_table_config)
        message_list = []

        for information in info_table_soup:

            contents = information.parent.contents

            info_date = contents[5].get_text()[-8:]
            info_msg = contents[7].contents[1].contents[0].get_text()
            msg_dict = {
                "date": info_date,
                "message": info_msg,
                "url": 'https://www.inscricao.marinha.mil.br/marinha/' + contents[7].contents[1].attrs['href'],
            }

            message_list.append(msg_dict)

        self.logger.info(msg=f"{len(message_list)} mensagens capturadas")

        timezone = pytz.timezone(zone=utils.get_config().get(section='timezone', option='PYTZ_TIMEZONE'))
        current_time = datetime.now(tz=timezone)

        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_data = {
            "title": title,
            "url": self.url,
            "acquisition_date": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "exam_date": stored_data["exam_date"],
            "messages": message_list,
            "last_update": stored_data["last_update"],
            "last_update_date": stored_data["last_update_date"]
        }

        self.logger.info(msg="Comparando com a aquisição do dia " + output_data["acquisition_date"] + "...")

        updated_messages = utils.list_difference(list_A=message_list, list_B=stored_data["messages"])

        if exam_date != stored_data["exam_date"]:
            self.logger.info(msg=f"Data do concurso atualizada para: {exam_date}")
            updated_messages.append({
                "date": current_time.strftime("%d/%m/%Y"),
                "message": f"Data do concurso atualizada para: {exam_date}",
                "url": self.url
            })
            output_data["exam_date"] = exam_date

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
            output_message (str): Mensagem de saída
        """
        bar_str = "\n-------------------------------\n"

        output_message = bar_str

        for info in message_list:
            info_str = info["date"] + " - "
            info_str += "<a href=\"" + info["url"] + "\">" + info['message'] + "</a>"
            info_str += bar_str

            output_message += info_str

        return output_message

    def updated_data(self):
        """
            Retorna os dados que foram atualizados
        Returns:
            output_message (str): Mensagem de saída
        """
        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        bar_str = "\n-------------------------------\n"

        output_message = str(len(stored_data["last_update"])) + " atualização(ões) obtida(s) para:\n"
        output_message += "<a href=\"" + stored_data['url'] + "\">"+ stored_data["title"] + "</a>"
        output_message += self.generate_message(message_list=stored_data["last_update"])

        return output_message

    def short_data(self):
        """
            Retorna os dados da página de forma resumida
        Returns:
            output_message (str): Mensagem de saída
        """

        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message = "<a href=\"" + stored_data["url"] + "\">" + stored_data["title"] + "</a>"
        output_message += "\nData do concurso: " + stored_data["exam_date"]
        output_message += self.generate_message(message_list=stored_data["messages"][0:3])
        output_message += 'Dados salvos no dia ' + stored_data['acquisition_date']

        return output_message

    def complete_data(self):
        """
            Retorna todos os dados salvos da página
        Returns:
            output_message (str): Mensagem de saída
        """
        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_message = "<a href=\"" + stored_data["url"] + "\">" + stored_data["title"] + "</a>"
        output_message += "\nData do concurso: " + stored_data["exam_date"]
        output_message += self.generate_message(message_list=stored_data["messages"])
        output_message += 'Dados salvos no dia ' + stored_data['acquisition_date']

        return output_message

    def force_acquisition(self):
        """
            Força uma aquisição e retorna uma mensagem se houve ou não dados atualizados
        Returns:
            output_message (str): Mensagem de saída
        """
        scrape_status = self.scrape_page()

        if scrape_status == 0:
            output_message = "Não foi possível fazer a aquisição"
        elif scrape_status == 1:
            output_message = "Não há dados novos capturados"
        elif scrape_status == 2:
            output_message = self.updated_data()

        return output_message

    def __repr__(self):
        return f"Scraper {self.name}: " \
               f"\n URL: {self.url}" \
               f"\n Database_path: {self.db_path}"


if __name__ == "__main__":
    """
        Rotina de teste do scraper, acessa a página, salva o arquivo e executa as
        funções da classe base
    """

    database_path = os.path.join(utils.get_data_path(), "cem2021.json")
    url = "https://www.inscricao.marinha.mil.br/marinha/index_concursos.jsp?id_concurso=401"
    cem2021 = MarinhaScraper(
        name="CP-CEM 2021",
        database_path=database_path,
        url=url
    )

    if cem2021.scrape_page():
        print("\n\nMensagem de atualização:")
        print(cem2021.updated_data())
        print("\n\nMensagem de resumo:")
        print(cem2021.short_data())
        print("\n\nMensagem completa: ")
        print(cem2021.complete_data())
    else:
        print("Erro no acesso à página")
