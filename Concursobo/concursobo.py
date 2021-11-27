import os
import re
import logging
import telegram.ext as tgm

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import Filters

from constants import BotMessages
from tinydb import TinyDB, Query
from Concursobo.scrapers.marinha_scraper import MarinhaScraper
from Concursobo import utils


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

        logging.basicConfig(format="%(asctime)s - %(name)s - %(message)s", level=logging.INFO,
                            datefmt="%d-%m-%Y %H:%M:%S")

        self.logger = logging.getLogger(name='Concursobô')

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
            self.logger.info(msg=f"Adicionando scraper {scraper.name} no bot")
            self.scrapers[scraper.name] = scraper

    def setup_handlers(self):
        """
            Cria os comandos do bot
        """

        # Começar
        self.dispatcher.add_handler(tgm.CommandHandler(command='start', callback=self.start_handler))
        # Ajuda
        self.dispatcher.add_handler(tgm.CommandHandler(command='ajuda', callback=self.help_handler))
        # Informações
        self.dispatcher.add_handler(tgm.CommandHandler(command='info', callback=self.info_handler))
        # Cadastrar chat
        self.dispatcher.add_handler(tgm.CommandHandler(command='cadastrar', callback=self.subscribe_handler))
        # Descadastrar chat
        self.dispatcher.add_handler(tgm.CommandHandler(command='descadastrar', callback=self.unsubscribe_handler))
        # Listar concursos
        self.dispatcher.add_handler(tgm.CommandHandler(command='listar_concursos', callback=self.list_scrapers))
        # Comandos concurso
        self.dispatcher.add_handler(tgm.CallbackQueryHandler(callback=self.button_actions))
        # Execução de comandos

        # Erro
        self.dispatcher.add_error_handler(callback=self.error_handler)

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
        pass

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
            update.message.reply_text(text=BotMessages.already_subscribed, parse_mode=ParseMode.HTML)
        else:
            self.contacts_list.insert({"chat_id": chat_id})
            update.message.reply_text(text=BotMessages.subscription_success, parse_mode=ParseMode.HTML)

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
            update.message.reply_text(text=BotMessages.unsubscription_success, parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text(text=BotMessages.not_subscribed, parse_mode=ParseMode.HTML)

    def list_scrapers(self, update, context):
        """
            Lista os scrapers e abre um teclado interativo
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        keyboard = [
            [InlineKeyboardButton(
                text=scraper_name,
                callback_data=f"\\scraper_selected:{scraper_name}"
            )]
            for scraper_name in self.scrapers
        ]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
        update.message.reply_text("Concursos cadastrados no bot:",
                                  reply_markup=reply_markup)

    def button_actions(self, update, context):
        """
            Lista as ações dos botões e as executa
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """
        command = update.callback_query.data
        scraper_selection = re.match(pattern=r"\\scraper_selected:(.*)", string=command)
        scraper_action = re.match(pattern=r"\\scraper_action:(.*)/(.*)", string=command)

        if scraper_selection:
            selected_scraper = scraper_selection.groups()[0]
            keyboard = [
                [InlineKeyboardButton(
                    text="Última atualização",
                    callback_data=f"\\scraper_action:{selected_scraper}/last_update"
                )],
                [InlineKeyboardButton(
                    text="Mostrar resumo dos dados",
                    callback_data=f"\\scraper_action:{selected_scraper}/short"
                )],
                [InlineKeyboardButton(
                    text="Mostrar todos os dados",
                    callback_data=f"\\scraper_action:{selected_scraper}/complete_data"
                )],
                [InlineKeyboardButton(
                    text="Forçar aquisição de dados",
                    callback_data=f"\\scraper_action:{selected_scraper}/force_acquisition"
                )],
            ]
            reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            update.callback_query.message.reply_text(f"Escolha uma ação para {selected_scraper}",
                                                     reply_markup=reply_markup)
        elif scraper_action:
            selected_scraper = scraper_action.groups()[0]
            selected_action = scraper_action.groups()[1]

            if selected_action == "last_update":
                message = self.scrapers[selected_scraper].updated_data()
                update.callback_query.message.reply_text(text=message, parse_mode=ParseMode.HTML)

            elif selected_action == "short":
                message = self.scrapers[selected_scraper].short_data()
                update.callback_query.message.reply_text(text=message, parse_mode=ParseMode.HTML)

            elif selected_action == "complete_data":
                message = self.scrapers[selected_scraper].complete_data()
                update.callback_query.message.reply_text(text=message, parse_mode=ParseMode.HTML)

            elif selected_action == "force_acquisition":
                scrape_status = self.scrapers[selected_scraper].scrape_page()
                if scrape_status == 0:
                    message = "Não foi possível fazer a aquisição"
                elif scrape_status == 1:
                    message = "Não há dados novos capturados"
                elif scrape_status == 2:
                    message = "Atualização obtida!\n" + self.scrapers[selected_scraper].updated_data()
                update.callback_query.message.reply_text(text=message, parse_mode=ParseMode.HTML)

            return


    def error_handler(self, update, context):
        """
            Gerencia os erros do bot
        Args:
            update (Update): Objeto com os dados do chat e do usuário.
            context (CallbackContext): Objeto de contexto.
        """

        self.logger.warning('Update "%s" causou o erro "%s"', update, context.error)

    def start_pooling(self):
        """
            Inicia o recebimento de comandos
        """

        self.logger.info(msg="Iniciando o recebimento de comandos")
        self.updater.start_polling()


if __name__ == "__main__":
    """
        Teste do bot: Cadastro de scraper, envio de uma mensagem e execução do bot para recepção de comandos
    """
    token = utils.get_config().get(section='telegram', option='BOT_TOKEN')
    contacts_path = os.path.join(utils.get_data_path(), "contacts_list.json")

    scraper_list = [
        MarinhaScraper(
            name="CP-CEM 2021",
            database_path=os.path.join(utils.get_data_path(), "cem2021.json"),
            url="https://www.inscricao.marinha.mil.br/marinha/index_concursos.jsp?id_concurso=401"
        )
    ]

    telegram_bot = TelegramBot(
        token=token,
        scraper_list=scraper_list,
        contacts_path=contacts_path
    )
    telegram_bot.start_pooling()
