from abc import ABC, abstractmethod
from typing import Dict, List, Union
from .stream import StreamInterface


class MessageInterface(ABC):
    """
    Интерфейс HTTP-сообщений (запросов и ответов).

    Сообщения считаются неизменяемыми - все методы, изменяющие состояние,
    должны возвращать новый экземпляр с измененными данными.

    Ссылки на стандарты:
    - RFC 7230: https://www.ietf.org/rfc/rfc7230.txt
    - RFC 7231: https://www.ietf.org/rfc/rfc7231.txt
    """

    @abstractmethod
    def get_protocol_version(self) -> str:
        """
        Получает версию HTTP-протокола.

        Возвращает:
            str: Версия протокола (например, "1.1", "1.0")
        """
        pass

    @abstractmethod
    def with_protocol_version(self, version: str) -> 'MessageInterface':
        """
        Создает копию сообщения с указанной версией протокола.

        Аргументы:
            version: Новая версия HTTP-протокола

        Возвращает:
            MessageInterface: Новый экземпляр с измененной версией протокола

        Исключения:
            ValueError: При недопустимой версии протокола
        """
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, List[str]]:
        """
        Получает все заголовки сообщения.

        Возвращает:
            Dict[str, List[str]]: Словарь, где ключи - имена заголовков,
                                 а значения - списки строковых значений
        """
        pass

    @abstractmethod
    def has_header(self, name: str) -> bool:
        """
        Проверяет наличие заголовка (без учета регистра).

        Аргументы:
            name: Имя заголовка (без учета регистра)

        Возвращает:
            bool: True если заголовок существует, иначе False
        """
        pass

    @abstractmethod
    def get_header(self, name: str) -> List[str]:
        """
        Получает все значения указанного заголовка.

        Аргументы:
            name: Имя заголовка (без учета регистра)

        Возвращает:
            List[str]: Список значений заголовка. Пустой список, если заголовка нет
        """
        pass

    @abstractmethod
    def get_header_line(self, name: str) -> str:
        """
        Получает значения заголовка в виде строки, разделенной запятыми.

        Аргументы:
            name: Имя заголовка (без учета регистра)

        Возвращает:
            str: Значения заголовка через запятую. Пустая строка, если заголовка нет
        """
        pass

    @abstractmethod
    def with_header(self, name: str, value: Union[str, List[str]]) -> 'MessageInterface':
        """
        Создает копию сообщения с заменой указанного заголовка.

        Аргументы:
            name: Имя заголовка (без учета регистра)
            value: Значение(я) заголовка (строка или список строк)

        Возвращает:
            MessageInterface: Новый экземпляр с измененным заголовком

        Исключения:
            ValueError: При недопустимом имени или значении заголовка
        """
        pass

    @abstractmethod
    def with_added_header(self, name: str, value: Union[str, List[str]]) -> 'MessageInterface':
        """
        Создает копию сообщения с добавлением значения к заголовку.

        Если заголовок не существует, он будет создан.

        Аргументы:
            name: Имя заголовка (без учета регистра)
            value: Значение(я) для добавления (строка или список строк)

        Возвращает:
            MessageInterface: Новый экземпляр с добавленным значением заголовка

        Исключения:
            ValueError: При недопустимом имени или значении заголовка
        """
        pass

    @abstractmethod
    def without_header(self, name: str) -> 'MessageInterface':
        """
        Создает копию сообщения без указанного заголовка.

        Аргументы:
            name: Имя удаляемого заголовка (без учета регистра)

        Возвращает:
            MessageInterface: Новый экземпляр без указанного заголовка
        """
        pass

    @abstractmethod
    def get_body(self) -> StreamInterface:
        """
        Получает тело сообщения.

        Возвращает:
            StreamInterface: Тело сообщения в виде потока
        """
        pass

    @abstractmethod
    def with_body(self, body: StreamInterface) -> 'MessageInterface':
        """
        Создает копию сообщения с указанным телом.

        Аргументы:
            body: Новое тело сообщения (должно быть StreamInterface)

        Возвращает:
            MessageInterface: Новый экземпляр с измененным телом

        Исключения:
            ValueError: Если тело невалидно
        """
        pass
