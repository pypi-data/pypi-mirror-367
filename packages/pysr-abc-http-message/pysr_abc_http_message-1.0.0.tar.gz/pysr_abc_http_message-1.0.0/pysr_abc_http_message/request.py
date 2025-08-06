from abc import ABC, abstractmethod
from .message import MessageInterface
from .uri import UriInterface


class RequestInterface(MessageInterface, ABC):
    """
    Интерфейс для исходящего HTTP-запроса от клиента.

    Содержит свойства согласно HTTP-спецификации:
    - Версия протокола
    - HTTP-метод
    - URI
    - Заголовки
    - Тело сообщения

    Запросы считаются неизменяемыми - все методы, изменяющие состояние,
    должны возвращать новый экземпляр.
    """

    @abstractmethod
    def get_request_target(self) -> str:
        """
        Получает цель запроса (request target).

        В большинстве случаев это будет путь URI, но может быть:
        - абсолютная форма (absolute-form)
        - форма authority (authority-form)
        - форма asterisk (asterisk-form)

        Возвращает:
            str: Цель запроса. Если не указана, возвращает "/"
        """
        pass

    @abstractmethod
    def with_request_target(self, request_target: str) -> 'RequestInterface':
        """
        Создает копию запроса с указанной целью запроса.

        Аргументы:
            request_target: Новая цель запроса

        Возвращает:
            RequestInterface: Новый экземпляр с измененной целью запроса

        Исключения:
            ValueError: При недопустимой цели запроса
        """
        pass

    @abstractmethod
    def get_method(self) -> str:
        """
        Получает HTTP-метод запроса.

        Возвращает:
            str: HTTP-метод (например, "GET", "POST")
        """
        pass

    @abstractmethod
    def with_method(self, method: str) -> 'RequestInterface':
        """
        Создает копию запроса с указанным HTTP-методом.

        Аргументы:
            method: Новый HTTP-метод (регистрозависимый)

        Возвращает:
            RequestInterface: Новый экземпляр с измененным методом

        Исключения:
            ValueError: При недопустимом HTTP-методе
        """
        pass

    @abstractmethod
    def get_uri(self) -> UriInterface:
        """
        Получает URI запроса.

        Возвращает:
            UriInterface: URI запроса
        """
        pass

    @abstractmethod
    def with_uri(self, uri: UriInterface, preserve_host: bool = False) -> 'RequestInterface':
        """
        Создает копию запроса с указанным URI.

        По умолчанию обновляет заголовок Host, если URI содержит host.
        Можно отключить это поведение через preserve_host=True.

        Аргументы:
            uri: Новый URI
            preserve_host: Если True, сохраняет оригинальный заголовок Host
                          когда он уже существует

        Возвращает:
            RequestInterface: Новый экземпляр с измененным URI

        Правила обновления Host:
        1. Если Host отсутствует/пустой и URI содержит host - обновляет Host
        2. Если Host отсутствует/пустой и URI не содержит host - не меняет Host
        3. Если Host существует и не пустой - не меняет Host (при preserve_host=True)
        """
        pass
