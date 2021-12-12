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


class CorridasBRScraper(BaseScraper):
    """
        Extrai os dados da página do CorridasBR
    """

    def __init__(self, name, database_path, base_url, table_url, max_distance):
        """
            Inicializa a classe
        Args:
            name (str): Nome do scraper
            database_path (str): Caminho para o arquivo onde estão salvos os dados
            base_url (str): URL base para os links da tabela do site CorridasBR
            table_url (str): URL da página do calendário de corridas do site CorridasBR
            max_distance (int): Distância máxima para filtrar as corridas
        """

        self.name = name
        self.db_path = database_path
        self.base_url = base_url
        self.table_url = table_url
        self.max_distance = max_distance

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(message)s",
            level=logging.INFO,
            datefmt="%d-%m-%Y %H:%M:%S",
        )

        self.logger = logging.getLogger(name=name)

    def check_distance(self, race_distances):
        """
            Checa se a distância da corrida é
        Args:
            race_distances (list of str): Lista contendo as distâncias de corridas
        Returns:
            validation (bool): Retorna verdadeiro se a corrida possui uma distância menor que a máxima
                distância definida
        """
        validation = False

        for distance in race_distances:
            if distance <= self.max_distance:
                validation = True

        return validation

    @staticmethod
    def group_races_by_city(month_races):
        """
            Agrupa as corridas de um mês por cidade, no formato do json de saída
        Args:
            month_races (list of dict): Corridas dessagrupadas
        Returns:
            grouped_races (list of dict): Corridas agrupadas por mês e por cidade
        """
        grouped_races = list()
        cities = sorted(set([race["city"] for race in month_races]))

        for city_name in cities:
            city_data = {"city": city_name, "races_list": list()}
            for race in month_races:
                if race["city"] == city_name:
                    city_data["races_list"].append(
                        {
                            "date": race["date"].strftime("%d/%m/%Y"),
                            "title": race["title"],
                            "url": race["url"],
                        }
                    )
            grouped_races.append(city_data)

        return grouped_races

    def group_races(self, races_list):
        """
            Agrupa as corridas por mês e depois por cidade, no formato do json de saída
        Args:
            races_list (list of dict): Corridas dessagrupadas
        Returns:
            grouped_races (list of dict): Corridas agrupadas por mês e por cidade
        """
        grouped_races = list()

        races_list = sorted(races_list.copy(), key=lambda race: race["date"])

        current_month = None

        for race in races_list:
            if race["date"].strftime("%m/%Y") != current_month:
                current_month = race["date"].strftime("%m/%Y")
                month_races = [
                    race
                    for race in races_list
                    if race["date"].strftime("%m/%Y") == current_month
                ]
                grouped_races.append(
                    {
                        "month": current_month,
                        "cities": self.group_races_by_city(month_races=month_races),
                    }
                )

        return grouped_races

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
            query_month = (
                s_month
                for s_month in stored_data
                if s_month["month"] == c_data["month"]
            )
            query_month = next(query_month, None)

            if query_month is not None:
                month_data = {"month": c_data["month"], "cities": list()}
                # Se há correspondência de mês, cada cidade será visualizada para ver
                # se existem novas corridas por cidade neste mês
                for city_races in c_data["cities"]:
                    query_city = (
                        s_city
                        for s_city in query_month["cities"]
                        if s_city["city"] == city_races["city"]
                    )
                    query_city = next(query_city, None)

                    if query_city is not None:
                        races_diff, _ = utils.list_difference(
                            list_A=city_races["races_list"],
                            list_B=query_city["races_list"],
                        )
                        if races_diff:
                            month_data["cities"].append(
                                {"city": city_races["city"], "races_list": races_diff}
                            )
                    else:
                        month_data["cities"].append(city_races)

                if month_data["cities"]:
                    difference.append(month_data)

            else:
                # Se há uma nova data salva
                difference.append(c_data)

        return difference

    def scrape_page(self):
        """
            Coleta os dados da página do concurso da Marinha
        Returns:
            (AcquisitionStatus): Indica o status da aquisição, se houve sucesso e / ou atualização dos dados
        """
        self.logger.info(msg="Acessando a página...")
        webpage = requests.get(url=self.table_url)

        if webpage.status_code != 200:
            self.logger.info(msg="Não foi possível acessar a página")
            return AcquisitionStatus.ERROR

        self.logger.info(msg="Página acessada, obtendo os dados...")

        soup = BeautifulSoup(markup=webpage.text, features="html.parser")

        tables_soup = soup.find_all(name="table", attrs={"width": "700"})

        # Título da página
        title = tables_soup[0].text.replace("\n", "")[:-1]

        rows_soup = tables_soup[1].findAll(name="tr", attrs={"height": "40"})
        races_list = list()

        for row_soup in rows_soup:

            row_data = row_soup.findAll(name="td")

            race_date = datetime.strptime(row_data[0].text, "%d/%m/%Y")
            race_city = row_data[1].text.strip()
            race_title = row_data[2].text.strip()

            if "km" in row_data[3].text:
                race_distances = row_data[3].text.replace("km", "").split("/")
                race_distances = sorted(
                    [float(distance.replace(",", ".")) for distance in race_distances]
                )
                if self.check_distance(race_distances=race_distances) is False:
                    continue
                distances_str = "/".join([str(d).replace(".0", "").replace(".", ",") for d in race_distances]) + "km"
            else:
                race_distances = [row_data[3].text]
                distances_str = "".join(race_distances)

            race_url = self.base_url + row_data[2].findAll(name="a")[0].attrs["href"]

            race_data = {
                "date": race_date,
                "city": race_city,
                "title": race_title + " - " + distances_str,
                "url": race_url,
            }

            races_list.append(race_data)

        self.logger.info(msg=f"{len(races_list)} corridas capturadas")

        timezone = pytz.timezone(
            zone=utils.get_config().get(section="timezone", option="PYTZ_TIMEZONE")
        )
        current_time = datetime.now(tz=timezone)

        grouped_races = self.group_races(races_list=races_list)

        with open(file=self.db_path, mode="r") as f:
            stored_data = json.load(f)

        output_data = {
            "title": title,
            "url": self.table_url,
            "acquisition_date": current_time.strftime("%d/%m/%Y %H:%M:%S"),
            "all_races": grouped_races,
            "last_update": stored_data["last_update"],
        }

        self.logger.info(
            msg="Comparando com a aquisição do dia "
            + stored_data["acquisition_date"]
            + "..."
        )

        updated_races = self.compare_new_with_old(
            current_data=grouped_races, stored_data=stored_data["all_races"]
        )

        if len(updated_races) == 0:
            self.logger.info(msg="Nenhuma alteração encontrada")

            with open(file=self.db_path, mode="w") as f:
                json.dump(output_data, f, indent=4)

            return AcquisitionStatus.UNCHANGED

        self.logger.info(msg=f"Alterações encontradas!")

        output_data["last_update"]["date"] = current_time.strftime("%d/%m/%Y %H:%M:%S")
        output_data["last_update"]["races_added"] = updated_races

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
        month_map = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }

        output_message_list = list()

        for month_races in message_list:
            month_str = month_races["month"][0:2]
            date_str = month_races["month"].replace(month_str + "/", month_map[month_str] + "/")
            output_message_list.append(
                f"\n<b>{date_str} ====================</b>\n"
            )
            for city in month_races["cities"]:
                output_message_list.append(
                    "\n<b>" + city["city"] + ":</b>\n"
                )

                for race in city["races_list"]:
                    output_message_list.append(
                        race["date"] + " - <a href=\"" + race["url"] + "\">" + race["title"] + "</a>\n"
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

        output_message_list.append(
            "Atualização obtida para:\n" + "<a href=\"" + stored_data["url"] + "\">" + stored_data["title"] + "</a>\n"
        )
        output_message_list.extend(
            self.generate_message(message_list=stored_data["last_update"]["races_added"])
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
            self.generate_message(message_list=stored_data["all_races"][0:3])
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
            self.generate_message(message_list=stored_data["all_races"])
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

    database_path = os.path.join(utils.get_data_path(), "corridasbr.json")
    base_url = "http://www.corridasbr.com.br/MG/"
    table_url = "http://www.corridasbr.com.br/MG/por_regiao.asp?regi%E3o=Metropolitana%20de%20Belo%20Horizonte"
    max_distance = 5

    corridasbr = CorridasBRScraper(
        name="CorridasBR",
        database_path=database_path,
        base_url=base_url,
        table_url=table_url,
        max_distance=max_distance,
    )

    status = corridasbr.scrape_page()

    if status:
        print("\n\nMensagem de atualização:")
        print(corridasbr.updated_data())
        print("\n\nMensagem de resumo:")
        print(corridasbr.short_data())
        print("\n\nMensagem completa: ")
        print(corridasbr.complete_data())
    else:
        print("Erro no acesso à página")
