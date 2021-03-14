"""
    Initializes webscrapper for debug purposes
"""
from configparser import ConfigParser

from MarinhoBot.web_scrapper import WebScrapper

if __name__ == '__main__':

    config_path = '../data/settings.cfg'
    cfg_parser = ConfigParser()
    cfg_parser.read(config_path)

    url = cfg_parser.get('web_scrapper_setup', 'URL')
    messages_path = '../data/stored_messages.json'

    scrapper = WebScrapper(url=url, message_data=messages_path)
    scrapper.parse_website()
    a = 0
