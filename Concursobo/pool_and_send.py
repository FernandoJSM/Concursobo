from Concursobo.telegram_bot import TelegramBot
from Concursobo.web_scraper import WebScraper


class PoolAndSend:
    """
        Class that runs the web scraper and updates the users if a new message is found
    """

    def __init__(self, url: str, token: str, message_data: str, contacts_list: str, pytz_timezone: str,
                 messages_per_minute: int):
        """
            Constructs the web scraper and telegram bot client
        Args:
            url: URL with the data to be scrapped.
            token: Token to access the bot.
            message_data: Path to store message data.
            contacts_list: Path to the file that manages contacts_list.
            pytz_timezone: Timezone info to be used in pytz.
            messages_per_minute: Number of messages to be sent each minute.
        """

        self.messages_per_minute = messages_per_minute
        self.telegram_bot = TelegramBot(token=token, message_data=message_data, contacts_list=contacts_list)
        self.web_scraper = WebScraper(url=url, message_data=message_data, pytz_timezone=pytz_timezone)
        self.check_and_send_messages()

    def check_and_send_messages(self, force_send=False):
        """
            Check for updates and send messages to all subscribers

        Args
            force_send: Boolean value that sends the message if there is no update
        """
        update_flag = self.web_scraper.parse_website()

        message_header = MessageHeader.force_send_true if force_send else MessageHeader.force_send_false

        if update_flag or force_send:
            self.telegram_bot.send_to_contact_list(header=message_header, messages_per_minute=self.messages_per_minute)


class MessageHeader:
    """
        Class with message data for the two cases of force_send variable
    """

    force_send_true = "Bom dia! Seguem a(s) última(s) atualizações do concurso:\n"
    force_send_false = "A página do concurso foi atualizada! Seguem a(s) última(s) atualizações do concurso:\n"