import csv
import json

import telegram.ext as tgm
import logging
from telegram import ParseMode


class TelegramBot:
    """
        Bot client class.
    """

    def __init__(self, token: str, message_data: str, contacts_list: str):
        """
            Constructs the Telegram bot client.
        Args:
            token: Token to access the bot.
            message_data: Path to store message data to be sent.
            contacts_list: Path to the file that manages contacts_list.
        """

        logging.basicConfig(format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO,
                            datefmt='%d-%m-%Y %H:%M:%S')

        self.logger = logging.getLogger(name='MarinhoBot')

        self.logger.info(msg='Setting up the bot')

        self.updater = tgm.Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        self.message_data = message_data
        self.contacts_list = contacts_list

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
        update.message.reply_text(text=BotMessages.start_msg, parse_mode=ParseMode.HTML)

    @staticmethod
    def help_handler(update, context):
        """
            Returns handlers explanation.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """
        update.message.reply_text(text=BotMessages.help_msg, parse_mode=ParseMode.HTML)

    def subscribe_handler(self, update, context):
        """
            Subscribe user/chat to the message list.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """

        chat_id = update.message.chat_id
        flag_subscribed = False

        with open(file=self.contacts_list, mode='r') as csv_file:
            contact_list = csv.reader(csv_file)

            for row in contact_list:
                if row == [str(chat_id)]:
                    flag_subscribed = True

        if flag_subscribed:
            update.message.reply_text(text=BotMessages.already_subscribed_msg, parse_mode=ParseMode.HTML)
        else:
            with open(file=self.contacts_list, mode='w') as csv_file:
                writer = csv.writer(csv_file, delimiter=',')
                writer.writerow([chat_id])

            update.message.reply_text(text=BotMessages.subscription_success_msg, parse_mode=ParseMode.HTML)

    def unsubscribe_handler(self, update, context):
        """
            Unsubscribe user/chat to the message list.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """

        chat_id = update.message.chat_id
        flag_subscribed = False
        filtered_contacts = []
        with open(file=self.contacts_list, mode='r') as csv_file:
            contact_list = csv.reader(csv_file)

            for row in contact_list:
                if row == [str(chat_id)]:
                    flag_subscribed = True
                else:
                    if row:
                        filtered_contacts.append(row[0])

        if flag_subscribed:
            # Erase file
            open(file=self.contacts_list, mode='w').close()

            # Rewrites file with filtered contacts
            with open(file=self.contacts_list, mode='w') as csv_file:
                writer = csv.writer(csv_file)
                for contact in filtered_contacts:
                    writer.writerow([contact])

            update.message.reply_text(text=BotMessages.unsubscription_success_msg, parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(text=BotMessages.not_subscribed_msg, parse_mode=ParseMode.HTML)

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

    def send_to_contact_list(self, header: str, messages_per_minute: int):
        """
            Sends the last three messages to all contacts of the contact list by the chat_id.
        Args:
            header: Header of the message.
            messages_per_minute: Number of messages to be sent each minute.
        """
        self.logger.info(msg)

    def last_update_handler(self, update, context):
        """
            Return last update from the web scraper service.
        Args:
            update: The update to gather chat/user id from.
            context: Context object.
        """

        message_to_send = self.get_messages(one_message=True)

        update.message.reply_text(text=message_to_send, parse_mode=ParseMode.HTML)

    def last_three_updates_handler(self, update, context):
        """
            Returns up to three latest updates from the web scraper service.
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

    start_msg = "Este é um bot desenvolvido para acompanhar as atualizações da página do concurso CP-CEM 2020 da " \
                "Marinha do Brasil.\r\n\r\n/help - Apresenta a explicação dos comandos\r\n/last_update - Apresent" \
                "a a última atualização da página do concurso\r\n/last_three_updates - Envia até as três últimas " \
                "atualizações da página do concurso\r\n/subscribe - Adiciona este chat na lista de assinantes\r\n" \
                "/unsubscribe - Remove este chat da lista de assinantes\r\n\r\nO bot foi programado na linguagem " \
                "Python, todo o projeto está no " + git_hub_url + "sob a " + license_url + ".\r\n"

    help_msg = start_msg

    already_subscribed_msg = "Você já está na lista de assinantes"
    subscription_success_msg = "Você foi adicionado na lista de assinantes"

    not_subscribed_msg = "Você não está na lista de assinantes"
    unsubscription_success_msg = "Você foi removido da lista de assinantes"
