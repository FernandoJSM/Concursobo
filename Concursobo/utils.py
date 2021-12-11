import os
import Concursobo
from configparser import ConfigParser


def get_data_path():
    """
        Retorna o caminho da pasta "data" do projeto
    Returns:
        data_path (str): Caminho da pasta "data" do projeto
    """
    package_folder = os.path.dirname(Concursobo.__file__)
    data_path = os.path.join(package_folder, "data")

    return data_path


def get_config():
    """
        Obtém o arquivo de configuração do projeto
    Returns:
        cfg_parser (ConfigParser): Arquivo do ConfigParser com os dados de configuração
    """
    package_folder = os.path.dirname(Concursobo.__file__)
    config_path = os.path.join(package_folder, "data/config.cfg")

    if os.path.isfile(config_path) is False:
        raise Exception(f"Arquivo {config_path} não encontrado!")

    cfg_parser = ConfigParser()
    cfg_parser.read(filenames=config_path)

    return cfg_parser


def list_difference(list_A, list_B):
    """
        Retorna a diferença do conteúdo de duas listas
    Args:
        list_A (list): Lista
        list_B (list): Lista

    Returns:
        diff_ab (list): Lista com a diferença da lista A com a lista B
        diff_ba (list): Lista com a diferença da lista B com a lista A
    """
    diff_ab = list()
    diff_ba = list()

    for element in list_A:
        if element not in list_B:
            diff_ab.append(element)

    for element in list_B:
        if element not in list_A:
            diff_ba.append(element)

    return diff_ab, diff_ba


def group_messages(message_list):
    """
        Agrupa as mensagens em grupos de até 4096 caracteres para o limite do Telegram
    Args:
        message_list (list of str): Lista com mensagens a serem enviadas
    Returns:
        output_message_list (list of str): Lista com as mensagens de saída
    """
    output_message_list = list()
    current_message = ""

    for message in message_list:
        if len(current_message + message) <= 4096:
            current_message += message
        else:
            output_message_list.append(current_message)
            current_message = message

    if len(current_message + message) <= 4096:
        output_message_list.append(current_message)

    return output_message_list
