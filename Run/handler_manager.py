from configparser import ConfigParser

from Concursobo.telegram_bot_legacy import TelegramBot

class HandlerManager:
    """
        Class to start the bot to manage input handlers
    """

    def __init__(self, token: str, message_data: str, contacts_list: str):
        """
            Starts the bot as a Handler Manager
        Args:
            token: Token to access the bot.
            message_data: Path to store message data
            contacts_list: Path to the file that manages contacts_list.
        """
        self.telegram_bot = TelegramBot(token=token, message_data=message_data, contacts_list=contacts_list)
        self.telegram_bot.start_pooling()


if __name__ == '__main__':

    config_path = r'/Concursobo/data\settings.cfg'
    cfg_parser = ConfigParser()
    cfg_parser.read(filenames=config_path)

    bot_token = cfg_parser.get(section='bot_setup', option='BOT_TOKEN')

    messages_path = r'/Concursobo/data\stored_messages.json'
    contacts_path = r'/Concursobo/data\contacts_list.csv'

    handler_bot = HandlerManager(token=bot_token, message_data=messages_path, contacts_list=contacts_path)
