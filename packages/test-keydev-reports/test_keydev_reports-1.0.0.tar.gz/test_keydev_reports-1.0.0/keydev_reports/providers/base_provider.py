from abc import ABC, abstractmethod
from typing import Iterable, Union


class BaseProvider(ABC):
    """
    Базовый класс для создания отчетов.
    """

    def __init__(self, data: Union[Iterable, dict], file_name: str):
        """
        Инициализатор класса.
        :param data: Данные для отчета.
        :param file_name: Путь к файлу.
        """
        self.data = data
        self.file_name = file_name


    @abstractmethod
    def export(self):
        """
        Метод для получения отчета.
        :return:
        """
        pass
    @classmethod
    def get_class_name(cls):
        """
        Метод для получения имени класса.
        :return:
        """
        return cls.__name__
