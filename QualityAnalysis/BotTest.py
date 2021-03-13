"""
    Initializes the bot for debug purposes
"""
from configparser import ConfigParser

if __name__ == '__main__':

    config_path = '../data/settings.cfg'
    cfg_parser = ConfigParser()
    cfg_parser.read(config_path)

    bot_token = cfg_parser.get('bot_setup', 'BOT_TOKEN')

    a = 1