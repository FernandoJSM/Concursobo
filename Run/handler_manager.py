from configparser import ConfigParser

from TelegramBot.telegram_bot import TelegramBot


class HandlerManager:
    """
        Class to start the bot to manage input handlers
    """

    def __init__(self, token: str, message_data: str):
        """
            Starts the bot as a Handler Manager
        Args:
            token: Token to access the bot.
            message_data: Path to store message d
        """
        self.telegram_bot = TelegramBot(token=token, message_data=message_data)
        self.telegram_bot.start_pooling()


if __name__ == '__main__':

    config_path = '../data/settings.cfg'
    cfg_parser = ConfigParser()
    cfg_parser.read(config_path)

    bot_token = cfg_parser.get('bot_setup', 'BOT_TOKEN')

    messages_path = '../data/stored_messages.json'

    handler_bot = HandlerManager(token=bot_token, message_data=messages_path)
