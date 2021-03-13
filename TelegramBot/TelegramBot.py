import telegram.ext as tgm
import logging


class TelegramBot:
    """
        Bot client class
    """

    def __init__(self, token: str):
        """
            Constructs the Telegram bot client
        Args:
            token: Token to access the bot
        """

        self.updater = tgm.Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.logger = logging
        self.logger.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO,
                                datefmt='%d-%m-%Y %H:%M:%S')

        self.setup_handlers()

    def setup_handlers(self):
        """
            Setup for bot handlers
        """

        insert_handlers = list

        # start
        insert_handlers.append(tgm.CommandHandler(command='start', callback=self.start_handler))
        # help
        insert_handlers.append(tgm.CommandHandler(command='help', callback=self.help_handler))
        # last update
        insert_handlers.append(tgm.CommandHandler(command='start', callback=self.last_update_handler))
        # last three updates
        insert_handlers.append(tgm.CommandHandler(command='start', callback=self.last_three_update_handler))

        for handler in insert_handlers:
            self.dispatcher.add_handler(handler)

    def start_pooling(self):
        """
            Starts the bot pooling
        """
        self.updater.start_polling()

    def start_handler(self):
        pass

    def help_handler(self):
        pass

    def last_update_handler(self):
        pass

    def last_three_update_handler(self):
        pass
