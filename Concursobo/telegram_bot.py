import re
import logging
import time
import utils

import telegram.ext as tgm
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from constants import BotMessages, AcquisitionStatus
from tinydb import TinyDB, Query


class TelegramBot:
    """
    Base do bot para o Telegram
    """

    def __init__(self, token: str, scraper_list: list, contacts_path: str):
        """
            Inicialiação da classe
        Args:
            token (str): Token para acessar o bot.
            scraper_list (list of BaseScraper): Lista contendo os scrapers utilizados no bot
            contacts_path (str): Caminho para o arquivo com a lista de contatos do bot
        """

        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(message)s",
            level=logging.INFO,
            datefmt="%d-%m-%Y %H:%M:%S",
        )

        self.logger = logging.getLogger(name="Concursobô")

        self.logger.info(msg="Configurando o bot...")

        self.updater = tgm.Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.messenger_bot = Bot(token=token)

        self.scrapers = dict()
        self.contacts_list = TinyDB(contacts_path)

        self.setup_handlers()

        self.add_scrapers(scraper_list=scraper_list)

    def add_scrapers(self, scraper_list):
        """
            Adiciona um scraper no bot
        Args
            scraper_list (list of BaseScraper): Lista contendo os scrapers utilizados no bot
        """

        for scraper in scraper_list:
            self.logger.info(msg=f"Adicionando scraper \"{scraper.name}\" no bot")
            self.scrapers[scraper.name] = scraper

    def setup_handlers(self):
        """
        Cria os comandos do bot
        """

        # Começar
        self.dispatcher.add_handler(
            tgm.CommandHandler(command="start", callback=self.start_handler)
        )
        # Ajuda
        self.dispatcher.add_handler(
            tgm.CommandHandler(command="ajuda", callback=self.help_handler)
        )
        # Informações
        self.dispatcher.add_handler(
            tgm.CommandHandler(command="info", callback=self.info_handler)
        )
        # Cadastrar chat
        self.dispatcher.add_handler(
            tgm.CommandHandler(command="cadastrar", callback=self.subscribe_handler)
        )
        # Descadastrar chat
        self.dispatcher.add_handler(
            tgm.CommandHandler(
                command="descadastrar", callback=self.unsubscribe_handler
            )
        )
        # Listar sites
        self.dispatcher.add_handler(
            tgm.CommandHandler(command="listar_sites", callback=self.list_scrapers)
        )
        # Atualizar tudo
        self.dispatcher.add_handler(
            tgm.CommandHandler(command="atualizar_tudo", callback=self.update_all)
        )
        # Comandos concurso
        self.dispatcher.add_handler(
            tgm.CallbackQueryHandler(callback=self.button_actions)
        )
        # Erro
        self.dispatcher.add_error_handler(callback=self.error_handler)

    @staticmethod
    def get_chat_id(update, context):
        """
            Retorna o chat_id do bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        Returns
            chat_id (int): ID do chat para enviar a mensagem
        """
        chat_id = None

        if update.message is not None:
            # from a text message
            chat_id = update.message.chat.id
        elif update.callback_query is not None:
            # from a callback message
            chat_id = update.callback_query.message.chat.id

        return chat_id

    @staticmethod
    def start_handler(update, context):
        """
            Retorna uma mensagem de boas vindas com a ajuda do bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        update.message.reply_text(text=BotMessages.start, parse_mode=ParseMode.HTML)

    @staticmethod
    def info_handler(update, context):
        """
            Retorna uma mensagem com informações sobre o bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        update.message.reply_text(text=BotMessages.info, parse_mode=ParseMode.HTML)

    @staticmethod
    def help_handler(update, context):
        """
            Retorna uma mensagem com os comandos do bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        update.message.reply_text(text=BotMessages.help, parse_mode=ParseMode.HTML)

    def subscribe_handler(self, update, context):
        """
            Adiciona o chat na lista de contatos do bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """

        chat_id = update.message.chat_id

        find_contacts = Query()

        if self.contacts_list.contains(find_contacts.chat_id == chat_id):
            update.message.reply_text(
                text=BotMessages.already_subscribed, parse_mode=ParseMode.HTML
            )
        else:
            self.contacts_list.insert({"chat_id": chat_id})
            update.message.reply_text(
                text=BotMessages.subscription_success, parse_mode=ParseMode.HTML
            )

    def unsubscribe_handler(self, update, context):
        """
            Remove o chat da lista de contatos do bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        chat_id = update.message.chat_id

        find_contacts = Query()

        if self.contacts_list.contains(find_contacts.chat_id == chat_id):
            contact = self.contacts_list.get(find_contacts.chat_id == chat_id)
            self.contacts_list.remove(doc_ids=[contact.doc_id])
            update.message.reply_text(
                text=BotMessages.unsubscription_success, parse_mode=ParseMode.HTML
            )
        else:
            update.message.reply_text(
                text=BotMessages.not_subscribed, parse_mode=ParseMode.HTML
            )

    def list_scrapers(self, update, context):
        """
            Lista os scrapers e abre um teclado interativo
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        keyboard = [
            InlineKeyboardButton(
                text=scraper_name, callback_data=f"\\scraper_selected:{scraper_name}",
            )
            for scraper_name in self.scrapers
        ]

        keyboard_splitted = utils.split_list(input_list=keyboard, size=2)

        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard_splitted)
        update.message.reply_text(
            "Concursos cadastrados no bot:", reply_markup=reply_markup
        )

    @staticmethod
    def force_acquisition(scraper):
        """
            Força uma aquisição e retorna uma mensagem se houve ou não dados atualizados
        Args:
            scraper (BaseScraper): Scraper para fazer a aquisição
        Returns:
            output_message_list (list of str): Lista com as mensagens de saída
            scraper_status (int): Status da aquisição
        """
        scraper_status = scraper.scrape_page()

        if scraper_status == AcquisitionStatus.ERROR:
            output_message_list = [
                f"Não foi possível fazer a aquisição para {scraper.name}"
            ]
        elif scraper_status == AcquisitionStatus.UNCHANGED:
            output_message_list = [f"Não há dados novos para {scraper.name}"]
        elif scraper_status == AcquisitionStatus.UPDATED:
            output_message_list = scraper.updated_data()

        return output_message_list, scraper_status

    def update_all(self, update, context):
        """
            Atualiza todos os scrapers cadastrados
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        for _, scraper in self.scrapers.items():
            message_list, _ = self.force_acquisition(scraper=scraper)
            self.return_messages(chat_id=self.get_chat_id(update=update, context=context), message_list=message_list)

    def return_messages(self, chat_id, message_list):
        """
            Envia mensagens para
        Args:
            chat_id (int): ID do chat para enviar a mensagem
            message_list (list of str): Lista contendo as mensagens a serem enviadas
        """
        for message in message_list:
            self.messenger_bot.sendMessage(
                chat_id=chat_id, text=message, parse_mode=ParseMode.HTML
            )

    def button_actions(self, update, context):
        """
            Lista as ações dos botões e as executa
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        command = update.callback_query.data
        update.callback_query.answer()
        scraper_selection = re.match(pattern=r"\\scraper_selected:(.*)", string=command)
        scraper_action = re.match(pattern=r"\\scraper_action:(.*)/(.*)", string=command)

        if scraper_selection:
            selected_scraper = scraper_selection.groups()[0]
            keyboard = [
                [
                    InlineKeyboardButton(
                        text="Última atualização",
                        callback_data=f"\\scraper_action:{selected_scraper}/last_update",
                    ),
                    InlineKeyboardButton(
                        text="Resumo dos dados",
                        callback_data=f"\\scraper_action:{selected_scraper}/short",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Todos os dados",
                        callback_data=f"\\scraper_action:{selected_scraper}/complete_data",
                    ),
                    InlineKeyboardButton(
                        text="Forçar aquisição",
                        callback_data=f"\\scraper_action:{selected_scraper}/force_acquisition",
                    ),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            update.callback_query.edit_message_text(
                f"{selected_scraper}", reply_markup=reply_markup
            )
        elif scraper_action:
            selected_scraper = scraper_action.groups()[0]
            selected_action = scraper_action.groups()[1]

            chat_id = self.get_chat_id(update=update, context=context)

            if selected_action == "last_update":
                message_list = self.scrapers[selected_scraper].updated_data()
                self.return_messages(chat_id=chat_id, message_list=message_list)

            elif selected_action == "short":
                message_list = self.scrapers[selected_scraper].short_data()
                self.return_messages(chat_id=chat_id, message_list=message_list)

            elif selected_action == "complete_data":
                message_list = self.scrapers[selected_scraper].complete_data()
                self.return_messages(chat_id=chat_id, message_list=message_list)

            elif selected_action == "force_acquisition":
                message_list, _ = self.force_acquisition(
                    scraper=self.scrapers[selected_scraper]
                )

                self.return_messages(chat_id=chat_id, message_list=message_list)

            return

    def error_handler(self, update, context):
        """
            Gerencia os erros do bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """

        self.logger.warning("Update \"%s\" causou o erro \"%s\"", update, context.error)

    def send_to_contact_list(self, message_list, messages_per_minute=50):
        """
            Envia uma mensagem para a lista de contatos
        Args:
            message_list (list of str): Lista de mensagens a serem enviadas
            messages_per_minute (int): Número de mensagens para serem enviadas por minuto (limite do Telegram)
        """
        self.logger.info(
            msg=f"Enviando mensagens para {str(len(self.contacts_list.all()))} contatos"
        )

        time_interval = messages_per_minute / 60

        for data in self.contacts_list.all():
            chat_id = data["chat_id"]
            for message in message_list:
                self.messenger_bot.sendMessage(
                    chat_id=chat_id, text=message, parse_mode=ParseMode.HTML
                )
                time.sleep(time_interval)

    def start_pooling(self):
        """
        Inicia o serviço de recebimento de comandos do bot
        """

        self.logger.info(msg="Iniciando o recebimento de comandos")
        self.updater.start_polling()

    def auto_check(self, scraper_name):
        """
            Coleta de dados e envio de mensagens para os assinantes da lista
        Args:
            scraper_name (str): Nome do scraper cadastrado no Concursobô
        """
        message_list, scraper_status = self.force_acquisition(
            scraper=self.scrapers[scraper_name]
        )

        if scraper_status == AcquisitionStatus.UPDATED:
            self.send_to_contact_list(message_list=message_list)
