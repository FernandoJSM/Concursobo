"""
    Initializes web scraper for debug purposes
"""
from configparser import ConfigParser

from Concursobo.web_scraper import WebScraper

if __name__ == '__main__':

    config_path = '../data/settings.cfg'
    cfg_parser = ConfigParser()
    cfg_parser.read(filenames=config_path)

    url = cfg_parser.get(section='web_scrapper_setup', option='URL')
    timezone = cfg_parser.get(section='web_scrapper_setup', option='PYTZ_TIMEZONE')
    messages_path = '../data/stored_messages.json'

    scrapper = WebScraper(url=url, message_data=messages_path, pytz_timezone=timezone)
    scrapper.parse_website()

    a = 0
