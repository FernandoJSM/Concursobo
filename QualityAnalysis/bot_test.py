"""
    Initializes the bot for debug purposes
"""
from configparser import ConfigParser

from TelegramBot.telegram_bot import TelegramBot

if __name__ == '__main__':

    config_path = '../data/settings.cfg'
    cfg_parser = ConfigParser()
    cfg_parser.read(config_path)

    bot_token = cfg_parser.get('bot_setup', 'BOT_TOKEN')
    messages_path = '../data/stored_messages.json'

    telegram_bot = TelegramBot(token=bot_token, message_data=messages_path)
    telegram_bot.start_pooling()

    a = 0
