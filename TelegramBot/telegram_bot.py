import json

import telegram.ext as tgm
import logging
from telegram import ParseMode

class TelegramBot:
    """
        Bot client class.
    """

    def __init__(self, token: str, message_data: str):
        """
            Constructs the Telegram bot client.
        Args:
            token: Token to access the bot.
            message_data: Path to store message data to be sent.
        """
        logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO,
                            datefmt='%d-%m-%Y %H:%M:%S')

        self.logger = logging.getLogger(name='TelegramBot')

        self.logger.info(msg='Setting up the bot')

        self.updater = tgm.Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.message_data = message_data

        self.setup_handlers()

    def setup_handlers(self):
        """
            Create bot handlers.
        """

        # start
        self.dispatcher.add_handler(tgm.CommandHandler(command='start', callback=self.start_handler))
        # help
        self.dispatcher.add_handler(tgm.CommandHandler(command='help', callback=self.help_handler))
        # subscribe
        self.dispatcher.add_handler(tgm.CommandHandler(command='subscribe', callback=self.subscribe_handler))
        # unsubscribe
        self.dispatcher.add_handler(tgm.CommandHandler(command='unsubscribe', callback=self.unsubscribe_handler))
        # last update
        self.dispatcher.add_handler(tgm.CommandHandler(command='last_update', callback=self.last_update_handler))
        # last three updates
        self.dispatcher.add_handler(tgm.CommandHandler(command='last_three_updates',
                                                       callback=self.last_three_updates_handler))
        # error handler
        self.dispatcher.add_error_handler(callback=self.error_handler)

    def start_pooling(self):
        """
            Starts the bot handler pooling.
        """

        self.logger.info(msg='Starting handler pooling')
        self.updater.start_polling()

    def read_messages(self):
        """
            Read the messages stored in the file, and returns them to be used.
        Returns:
            stored_messages: Dictionary with all data retrieved from the file.
        """

        with open(file=self.message_data, mode='r') as json_file:
            messages_dict = json.load(fp=json_file)

        return messages_dict

    @staticmethod
    def start_handler(update, context):
        """
            Returns welcome message and handlers explanation.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        update.message.reply_text(text=BotMessages.start_message, parse_mode=ParseMode.HTML)

    @staticmethod
    def help_handler(update, context):
        """
            Returns handlers explanation.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        update.message.reply_text(text=BotMessages.help_message, parse_mode=ParseMode.HTML)

    @staticmethod
    def subscribe_handler(update, context):
        """
            Subscribe user/chat to the message list.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    @staticmethod
    def unsubscribe_handler(update, context):
        """
            Unsubscribe user/chat to the message list.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        pass

    def get_messages(self, one_message):
        """
            Gets the messages from the input file and return the message to be sent to the user.
        Args:
            one_message: Indicates if only one message is returned. If false, returns up to three messages.
        Returns:
            message_to_send: Message to be sent to the user
        """

        messages_dict = self.read_messages()

        url_str = '<a href=\"' + messages_dict['url'] + '\">Página do concurso</a>'
        header_str = messages_dict['title'] + '\n' + url_str
        bar_str = '\n-------------------------------\n'
        message_to_send = header_str + bar_str

        if one_message:
            messages_keys = ['last_message']
        else:
            messages_keys = ['last_message', 'penultimate_message', 'antepenultimate_message']

        for key in messages_keys:
            if messages_dict[key]['message'] != '':
                msg_url_str = '<a href=\"' + messages_dict[key]['link'] + '\">' + \
                              messages_dict[key]['message'] + '</a>'
                message_str = messages_dict[key]['date'] + '\n' + msg_url_str
                message_to_send += message_str + bar_str

        footer_str = 'Dados salvos no dia ' + messages_dict['acquired_date']

        message_to_send += footer_str

        return message_to_send

    def last_update_handler(self, update, context):
        """
            Return last update from the webscrapper service.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """

        message_to_send = self.get_messages(one_message=True)

        update.message.reply_text(text=message_to_send, parse_mode=ParseMode.HTML)

    def last_three_updates_handler(self, update, context):
        """
            Returns up to three latest updates from the webscrapper service.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """

        message_to_send = self.get_messages(one_message=False)

        update.message.reply_text(text=message_to_send, parse_mode=ParseMode.HTML)

    def error_handler(self, update, context):
        """
            Handles bot errors and add to the logger.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """

        self.logger.warning('Update "%s" caused error "%s"', update, context.error)


class BotMessages:
    """
        Class to store standard messages from the bot.
    """

    git_hub_url = '<a href=\"https://github.com/FernandoJSM/MarinhoBot\">GitHub</a>'

    license_url = '<a href=\"https://github.com/FernandoJSM/MarinhoBot/blob/main/LICENSE\">licença GPL-2.0</a>'

    start_message = "Este é um bot desenvolvido para acompanhar as atualizações da página do concurso CP-CEM 2020 da " \
                    "Marinha do Brasil.\r\n\r\n/help - Apresenta a explicação dos comandos\r\n/last_update - Apresent" \
                    "a a última atualização da página do concurso\r\n/last_three_updates - Envia até as três últimas " \
                    "atualizações da página do concurso\r\n\r\nO bot foi programado na linguagem Python, todo o proje" \
                    "to está no " + git_hub_url + "sob a  " + license_url + ".\r\n"

    help_message = start_message
