from typing import Any, Union
from abc import ABC, abstractmethod


class ContainerInterface(ABC):
    """
    Описывает интерфейс контейнера, который предоставляет методы для чтения его записей.
    """

    @abstractmethod
    def get(self, name: Union[str, type]) -> Any:
        """
        Находит запись в контейнере по идентификатору и возвращает её.

        :param name: Идентификатор записи для поиска
        :raises NotFoundExceptionInterface: Если запись не найдена
        :raises ContainerExceptionInterface: Ошибка при получении записи
        :return: Запись любого типа
        """
        pass

    @abstractmethod
    def has(self, name: Union[str, type]) -> bool:
        """
        Возвращает True, если контейнер может вернуть запись по данному идентификатору.
        Возвращает False в противном случае.

        Возврат True не гарантирует, что get(name) не вызовет исключение.
        Однако это означает, что get(name) не вызовет NotFoundExceptionInterface.

        :param name: Идентификатор записи для проверки
        :return: bool
        """
        pass


class ContainerErrorInterface(ABC):
    """
    Общее исключение в контейнере.
    """
    pass


class NotFoundErrorInterface(ContainerErrorInterface, ABC):
    """
    Запись не найдена в контейнере.
    """
    pass