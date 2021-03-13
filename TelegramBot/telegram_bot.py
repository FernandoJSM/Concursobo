import json

import telegram.ext as tgm
import logging


class TelegramBot:
    """
        Bot client class.
    """

    def __init__(self, token: str, message_data: str):
        """
            Constructs the Telegram bot client.
        Args:
            token: Token to access the bot.
            message_data: Path to store message data to be sent
        """

        self.updater = tgm.Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.message_data = message_data

        self.logger = logging.getLogger(name='TelegramBot')
        logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO,
                            datefmt='%d-%m-%Y %H:%M:%S')

        self.setup_handlers()

    def setup_handlers(self):
        """
            Setup for bot handlers.
        """

        insert_handlers = list

        # start
        insert_handlers.append(tgm.CommandHandler(command='start', callback=self.start_handler))
        # help
        insert_handlers.append(tgm.CommandHandler(command='help', callback=self.help_handler))
        # subscribe
        insert_handlers.append(tgm.CommandHandler(command='subscribe', callback=self.subscribe_handler))
        # unsubscribe
        insert_handlers.append(tgm.CommandHandler(command='unsubscribe', callback=self.unsubscribe_handler))
        # last update
        insert_handlers.append(tgm.CommandHandler(command='last_update', callback=self.last_update_handler))
        # last three updates
        insert_handlers.append(tgm.CommandHandler(command='last_three_updates',
                                                  callback=self.last_three_updates_handler))

        for handler in insert_handlers:
            self.dispatcher.add_handler(handler)

        self.dispatcher.add_error_handler(callback=self.error_handler)

    def start_pooling(self):
        """
            Starts the bot handler pooling.
        """

        self.updater.start_polling()

    def start_handler(self, update: tgm.Update, context: tgm.CallbackContext):
        """
            Returns welcome message and handlers explanation.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    def help_handler(self, update: tgm.Update, context: tgm.CallbackContext):
        """
            Returns handlers explanation.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    def subscribe_handler(self, update: tgm.Update, context: tgm.CallbackContext):
        """
            Subscribe user/chat to the message list.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    def unsubscribe_handler(self, update: tgm.Update, context: tgm.CallbackContext):
        """
            Unsubscribe user/chat to the message list.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    def last_update_handler(self, update: tgm.Update, context: tgm.CallbackContext):
        """
            Return last update from the webscrapper service.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    def last_three_updates_handler(self, update: tgm.Update, context: tgm.CallbackContext):
        """
            Returns up to three latest updates from the webscrapper service.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    def error_handler(self, update: tgm.Update, context: tgm.CallbackContext):
        """
            Handles bot errors and add to the logger.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """

        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def read_messages(self):
        """
            Read the messages stored in the file, and returns them to be used.
        Returns:
            stored_messages: Dictionary with all data retrieved from the file.
        """

        with open(self.message_data) as json_file:
            messages_dict = json.load(json_file)

        return messages_dict
