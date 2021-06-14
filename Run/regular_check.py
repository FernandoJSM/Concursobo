from configparser import ConfigParser

from Concursobo.pool_and_send import PoolAndSend

if __name__ == '__main__':
    """
        Runs the pool and send method and send messages only if there is an update
    """

    config_path = '../data/settings.cfg'
    cfg_parser = ConfigParser()
    cfg_parser.read(filenames=config_path)

    url = cfg_parser.get(section='web_scrapper_setup', option='URL')
    timezone = cfg_parser.get(section='web_scrapper_setup', option='PYTZ_TIMEZONE')
    bot_token = cfg_parser.get(section='bot_setup', option='BOT_TOKEN')

    messages_path = '../data/stored_messages.json'
    contacts_path = '../data/contacts_list.csv'

    messages_per_minute = 50

    pas = PoolAndSend(url=url, token=bot_token, message_data=messages_path, contacts_list=contacts_path,
                      pytz_timezone=timezone, messages_per_minute=messages_per_minute)

    pas.check_and_send_messages(force_send=False)
