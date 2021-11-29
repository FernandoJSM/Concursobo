from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """
    Classe de base para os scrapers implementados no código
    """

    @abstractmethod
    def scrape_page(self):
        """
        Coleta os dados da página do concurso
        """
        pass

    @abstractmethod
    def updated_data(self):
        """
        Retorna os dados que foram atualizados
        """
        pass

    @abstractmethod
    def short_data(self):
        """
        Retorna os dados da página de forma resumida
        """
        pass

    @abstractmethod
    def complete_data(self):
        """
        Retorna todos os dados salvos da página
        """
        pass
