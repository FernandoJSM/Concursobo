import json
import logging
import os
import re
from datetime import datetime

import pytz
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode

from Concursobo.scrapers.base_scraper import BaseScraper
from Concursobo import utils
from Concursobo.constants import AcquisitionStatus


class PCIScraper(BaseScraper):
    """
    Extrai os dados da página de notícias do site PCI concursos
    """

    def __init__(self, name, database_path, store_size, keywords, ignore_words):
        """
            Inicializa a classe
        Args:
            name (str): Nome do scraper
            database_path (str): Caminho para o arquivo onde estão salvos os dados
            store_size (int): Quantidade de dias armazenados no banco de dados
            keywords (list of str): Lista de palavras que a notícia deve conter pelo menos uma
            ignore_words (list of str): Lista de palavras para descartar uma notícia
        """

        self.name = name
        self.db_path = database_path
        self.store_size = store_size
        self.url = "https://www.pciconcursos.com.br/noticias/"
        self.keywords = keywords
        self.ignore_words = ignore_words

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(message)s",
            level=logging.INFO,
            datefmt="%d-%m-%Y %H:%M:%S",
        )

        self.logger = logging.getLogger(name=name)

    def job_scrape(self, job, saved_jobs, session):
        """
            Raises
        Args:
            job (Tag): Tag do BeautifulSoup descrevendo um concurso encontrado
            saved_jobs (list of dict): Lista que contém os concursos salvos
            session (Session): Sessão de acesso ao site
        """
        job_website = session.get(job.attrs["href"]).text

        job_title = unidecode(job["title"])
        for word in self.ignore_words:
            if job_title.lower().find(word.lower()) != -1:
                return

        soup = BeautifulSoup(job_website, "html.parser")
        page_data = soup.find_all("div", {"itemprop": "articleBody"})

        article = unidecode(page_data[0].text.lower())

        matched_keywords = list()
        for keyword in self.keywords:
            if article.find(keyword.lower()) != -1:
                matched_keywords.append(keyword)

        if matched_keywords or len(self.keywords) == 0:
            job_data = {
                "title": job.attrs["title"],
                "url": job.attrs["href"],
                "keywords": matched_keywords,
            }

            saved_jobs.append(job_data)

    @staticmethod
    def process_saved_data(saved_data):
        """
            Processa os dados salvos para o json de saída
        Args:
            saved_data (dict): Dados extraídos do site organizados
        Returns:
            output_data (list of dict): Dados de saída processados
        """
        output_data = list()

        for date, jobs_list in saved_data.items():
            output_data.append(
                {"date": date.strftime("%d/%m/%Y"), "jobs_list": jobs_list}
            )

        return output_data

    @staticmethod
    def compare_new_with_old(current_data, stored_data):
        """
            Compara os dados novos com os antigos e retorna a diferença entre as duas listas de entrada
        Args:
            current_data (list of dict): Dados capturados para serem comparados com os dados antigos
            stored_data (list of dict): Dados armazenados
        Returns:
            difference (list of dict): Lista com os dados diferentes entre as listas
        """
        difference = list()

        for c_data in current_data:
            query_date = (
                s_data for s_data in stored_data if s_data["date"] == c_data["date"]
            )
            query_match = next(query_date, None)

            if query_match is not None:
                # Se há correspondência de datas, será capturada a diferença entre elas
                jobs_diff, _ = utils.list_difference(
                    list_A=c_data["jobs_list"], list_B=query_match["jobs_list"]
                )
                if jobs_diff:
                    difference.append({"date": c_data["date"], "jobs_list": jobs_diff})
            else:
                # Se há uma nova data salva
                if c_data["jobs_list"]:
                    difference.append(c_data)

        return difference

    def scrape_page(self):
        """
            Coleta os dados da página de notícias do PCI Concursos
        Returns:
            (AcquisitionStatus): Indica o status da aquisição, se houve sucesso e / ou atualização dos dados
        """
        session = requests.Session()

        current_page = 1
        saved_data = dict()

        while len(saved_data) < self.store_size:
            self.logger.info(msg=f"Acessando a página {current_page}...")
            webpage = session.get(url=self.url + str(current_page))
            if webpage.status_code != 200:
                self.logger.info(msg="Não foi possível acessar a página")
                return AcquisitionStatus.ERROR

            self.logger.info(msg=f"Página {current_page} acessada, obtendo os dados...")

            soup = BeautifulSoup(markup=webpage.text, features="html.parser")

            page_data = soup.find_all(["h2", "ul"])

            news_date = None
            saved_jobs = list()
            for data in page_data:
                date_match = re.match(
                    pattern=r"[0-9]{2}/[0-9]{2}/[0-9]{2}", string=data.text
                )

                if "principal" in data.attrs.get("class", list()) and date_match:
                    news_date = datetime.strptime(date_match.string, "%d/%m/%Y")
                    saved_jobs = list()

                if "noticias" in data.attrs.get("class", list()) and (
                    news_date is not None
                ):
                    jobs = data.find_all("a")
                    self.logger.info(
                        f"Processando o dia {str(news_date.date())} ("
                        + str(len(jobs))
                        + " notícias)..."
                    )
                    for job in jobs:
                        self.job_scrape(job=job, saved_jobs=saved_jobs, session=session)

                    if saved_jobs:
                        self.logger.info(f"{len(saved_jobs)} notícias encontradas!")

                    if news_date in saved_data:
                        saved_data[news_date].extend(saved_jobs)
                    else:
                        saved_data[news_date] = saved_jobs

                    if len(saved_data) >= self.store_size:
                        break

            current_page += 1

        timezone = pytz.timezone(
            zone=utils.get_config().get(section="timezone", option="PYTZ_TIMEZONE")
        )
        current_time = datetime.now(tz=timezone)

        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        all_jobs = self.process_saved_data(saved_data=saved_data)

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

        updated_data = self.compare_new_with_old(
            current_data=all_jobs, stored_data=stored_data["all_jobs"]
        )

        if len(updated_data) == 0:
            self.logger.info(msg="Nenhuma alteração encontrada")

            with open(file=self.db_path, mode="w") as f:
                json.dump(output_data, f, indent=4)

            return AcquisitionStatus.UNCHANGED

        self.logger.info(msg=f"{len(updated_data)} alterações encontradas!")

        output_data["last_update"] = {
            "date": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "updated_data": updated_data,
        }

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
        output_message_list = list()

        for date_info in message_list:

            output_message_list.append(
                "\n<b>" + date_info["date"] + " ====================</b>\n\n"
            )

            for info in date_info["jobs_list"]:
                output_message_list.append(
                    '<a href="' + info["url"] + '">' + info["title"] + "</a>"
                )
                output_message_list.append(
                    "\n<b>Palavras-chave:</b> " + ", ".join(info["keywords"]) + "\n\n"
                )

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

        if len(stored_data["last_update"]["updated_data"]) == 1:
            output_message_list.append(
                (
                    str(len(stored_data["last_update"]["updated_data"]))
                    + " atualização obtida para:\n"
                )
            )
        else:
            output_message_list.append(
                (
                    str(len(stored_data["last_update"]["updated_data"]))
                    + " atualizações obtidas para:\n"
                )
            )

        output_message_list.append(
            '<a href="' + stored_data["url"] + '">' + self.name + "</a>:\n"
        )
        output_message_list.extend(
            self.generate_message(message_list=stored_data["last_update"]["updated_data"])
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
            ('<a href="' + stored_data["url"] + '">' + self.name + "</a>")
        ]

        filtered_jobs = [data for data in stored_data["all_jobs"] if data["jobs_list"]]

        if len(filtered_jobs) > 3:
            filtered_jobs = filtered_jobs[0:3]

        output_message_list.extend(self.generate_message(message_list=filtered_jobs))
        output_message_list.append(
            "<b>Dados salvos no dia " + stored_data["acquisition_date"] + "</b>"
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
            ('<a href="' + stored_data["url"] + '">' + self.name + "</a>")
        ]

        filtered_jobs = [data for data in stored_data["all_jobs"] if data["jobs_list"]]

        output_message_list.extend(self.generate_message(message_list=filtered_jobs))
        output_message_list.append(
            "<b>Dados salvos no dia " + stored_data["acquisition_date"] + "</b>"
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

    database_path = os.path.join(utils.get_data_path(), "pci.json")
    store_size = 2

    keywords = [
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
    ]
    ignore_words = ["estagio", "estagiario", "aprendiz", "suspens"]

    pci = PCIScraper(
        name="PCI Concursos",
        database_path=database_path,
        store_size=store_size,
        keywords=keywords,
        ignore_words=ignore_words,
    )

    status = pci.scrape_page()

    if status:
        print("\n\nMensagem de atualização:")
        print(pci.updated_data())
        print("\n\nMensagem de resumo:")
        print(pci.short_data())
        print("\n\nMensagem completa: ")
        print(pci.complete_data())
    else:
        print("Erro no acesso à página")
