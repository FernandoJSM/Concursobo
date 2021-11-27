import os
import Concursobo
from configparser import ConfigParser
from enum import IntEnum


class AcquisitionStatus(IntEnum):
    """
        Indica o status da aquisição dos dados
    """
    ERROR = 0           # Não foi possível acessar a página
    UNCHANGED = 1       # A página foi acessada, mas os dados não foram alterados
    UPDATED = 2         # Os dados foram atualizados


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
        Retorna a diferença do conteúdo da lista A comparado com a lista B
    Args:
        list_A (list): Lista
        list_B (list): Lista

    Returns:
        diff (list): Lista com a diferença da lista A com a lista B
    """
    diff = list()

    for element in list_A:
        if element not in list_B:
            diff.append(element)

    return diff
