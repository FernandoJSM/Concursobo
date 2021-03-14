import json
import logging
import pytz
import requests
from datetime import datetime
from bs4 import BeautifulSoup


class WebScraper:
    """
        Class with the website scrapper methods, specific to the Brazilian Navy staff selection page.
    """

    def __init__(self, url: str, message_data: str, pytz_timezone: str):
        """
            Constructs the web scraper object
        Args:
            url: URL with the data to be scrapped.
            message_data: Path to store message data to be saved.
            pytz_timezone: Timezone info to be used in pytz
        """
        logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO,
                            datefmt='%d-%m-%Y %H:%M:%S')

        self.logger = logging.getLogger(name='Web Scraper')
        self.url = url
        self.message_data = message_data
        self.timezone = pytz_timezone
        self.page = None

    def get_page(self):
        """
            Get data from the url and saves it in the page attribute

        Returns
            data_obtained: Boolean value indicating if the data is obtained
        """

        self.logger.info(msg='Retrieving url data')
        self.page = requests.get(url=self.url)

        if self.page.status_code == 200:
            self.logger.info(msg='URL data obtained')
            data_obtained = True
        else:
            self.logger.info(msg='Not possible to get the data')
            data_obtained = False
            self.page = None

        return data_obtained

    def parse_website(self):
        """
            Parse the input data according to the Brazilian Navy staff selection page and saves it on the messages
            file.

        Returns:
            new_message_flag: Flag that indicates if a new message is found
        """

        data_obtained = self.get_page()

        if not data_obtained:
            return

        soup = BeautifulSoup(markup=self.page.content, features='html.parser')

        title_soup = soup.find_all(name="span", class_="header0")

        title = title_soup[0].contents[0].get_text()

        info_table_config = {
            'height': '24',
            'width': '46',
            'align': 'right',
            'valign': 'middle',
        }

        info_table_soup = soup.findAll(name='td', attrs=info_table_config)

        messages_list = []
        number_of_messages = 3 if len(info_table_soup) > 3 else len(info_table_soup)

        if number_of_messages == 0:
            return

        self.logger.info(msg='Found ' + str(len(info_table_soup)) + ' messages, saving ' + str(number_of_messages)
                             + ' messages')

        for message_index in range(number_of_messages):

            contents = info_table_soup[message_index].parent.contents

            info_date = contents[5].get_text()[-8:]
            info_msg = contents[7].contents[1].contents[0].get_text()
            msg_dict = {
                "date": info_date,
                "message": info_msg,
                "link": 'https://www.inscricao.marinha.mil.br/marinha/' + contents[7].contents[1].attrs['href'],
            }

            messages_list.append(msg_dict)

        blank_msg_dict = {
            "message": '',
            "message_link": '',
        }

        if len(messages_list) == 1:
            messages_list.append(blank_msg_dict)
        if len(messages_list) == 2:
            messages_list.append(blank_msg_dict)

        get_timezone = pytz.timezone(zone=self.timezone)
        corrected_time = datetime.now(tz=get_timezone)

        saved_messages = {
            "title": title,
            "url": self.url,
            "acquired_date": corrected_time.strftime("%d/%m/%Y %H:%M:%S"),
            "last_message": messages_list[0],
            "penultimate_message": messages_list[1],
            "antepenultimate_message": messages_list[2]
        }

        with open(file=self.message_data, mode='r') as json_file:
            old_data = json.load(fp=json_file)

        if old_data['last_message'] != saved_messages['last_message']:
            self.logger.info(msg='New message found')
            new_message_flag = True
        else:
            self.logger.info(msg='No message found')
            new_message_flag = False

        self.logger.info(msg='Saving data to the file')
        with open(file=self.message_data, mode='w') as json_file:
            json.dump(obj=saved_messages, fp=json_file, indent=4)

        return new_message_flag
