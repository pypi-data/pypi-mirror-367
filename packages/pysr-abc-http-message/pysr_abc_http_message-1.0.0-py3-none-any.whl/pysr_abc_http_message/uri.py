from abc import ABC, abstractmethod
from typing import Optional


class UriInterface(ABC):
    """
    Интерфейс для представления URI в соответствии с RFC 3986.

    Этот интерфейс предоставляет методы для работы с компонентами URI и выполнения
    наиболее распространенных операций. Все экземпляры считаются неизменяемыми -
    методы, изменяющие состояние, должны возвращать новый экземпляр.

    Основное использование - HTTP запросы, но может применяться и в других контекстах.
    """

    @abstractmethod
    def get_scheme(self) -> str:
        """
        Получить схему URI.

        Возвращает:
            str: Схема URI в нижнем регистре. Пустая строка, если схема отсутствует.
        """
        pass

    @abstractmethod
    def get_authority(self) -> str:
        """
        Получить компонент authority URI.

        Возвращает:
            str: Authority в формате "[user-info@]host[:port]". Пустая строка, если отсутствует.
        """
        pass

    @abstractmethod
    def get_user_info(self) -> str:
        """
        Получить информацию о пользователе.

        Возвращает:
            str: Информация о пользователе в формате "username[:password]". Пустая строка, если отсутствует.
        """
        pass

    @abstractmethod
    def get_host(self) -> str:
        """
        Получить хост URI.

        Возвращает:
            str: Хост в нижнем регистре. Пустая строка, если отсутствует.
        """
        pass

    @abstractmethod
    def get_port(self) -> Optional[int]:
        """
        Получить порт URI.

        Возвращает:
            Optional[int]: Порт как целое число или None, если порт стандартный для схемы или отсутствует.
        """
        pass

    @abstractmethod
    def get_path(self) -> str:
        """
        Получить путь URI.

        Возвращает:
            str: Путь с percent-encoding, но без двойного кодирования.
        """
        pass

    @abstractmethod
    def get_query(self) -> str:
        """
        Получить строку запроса URI.

        Возвращает:
            str: Строка запроса (без ведущего "?"). Пустая строка, если отсутствует.
        """
        pass

    @abstractmethod
    def get_fragment(self) -> str:
        """
        Получить фрагмент URI.

        Возвращает:
            str: Фрагмент (без ведущего "#"). Пустая строка, если отсутствует.
        """
        pass

    @abstractmethod
    def with_scheme(self, scheme: str) -> 'UriInterface':
        """
        Создать новый экземпляр с указанной схемой.

        Аргументы:
            scheme: Новая схема URI

        Возвращает:
            UriInterface: Новый экземпляр с измененной схемой

        Исключения:
            ValueError: Если схема недопустима или не поддерживается
        """
        pass

    @abstractmethod
    def with_user_info(self, user: str, password: Optional[str] = None) -> 'UriInterface':
        """
        Создать новый экземпляр с указанной информацией о пользователе.

        Аргументы:
            user: Имя пользователя
            password: Пароль (опционально)

        Возвращает:
            UriInterface: Новый экземпляр с измененной информацией о пользователе
        """
        pass

    @abstractmethod
    def with_host(self, host: str) -> 'UriInterface':
        """
        Создать новый экземпляр с указанным хостом.

        Аргументы:
            host: Новый хост

        Возвращает:
            UriInterface: Новый экземпляр с измененным хостом

        Исключения:
            ValueError: Если хост недопустим
        """
        pass

    @abstractmethod
    def with_port(self, port: Optional[int]) -> 'UriInterface':
        """
        Создать новый экземпляр с указанным портом.

        Аргументы:
            port: Новый порт или None для удаления порта

        Возвращает:
            UriInterface: Новый экземпляр с измененным портом

        Исключения:
            ValueError: Если порт вне допустимого диапазона
        """
        pass

    @abstractmethod
    def with_path(self, path: str) -> 'UriInterface':
        """
        Создать новый экземпляр с указанным путем.

        Аргументы:
            path: Новый путь

        Возвращает:
            UriInterface: Новый экземпляр с измененным путем

        Исключения:
            ValueError: Если путь недопустим
        """
        pass

    @abstractmethod
    def with_query(self, query: str) -> 'UriInterface':
        """
        Создать новый экземпляр с указанной строкой запроса.

        Аргументы:
            query: Новая строка запроса (без ведущего "?")

        Возвращает:
            UriInterface: Новый экземпляр с измененной строкой запроса

        Исключения:
            ValueError: Если строка запроса недопустима
        """
        pass

    @abstractmethod
    def with_fragment(self, fragment: str) -> 'UriInterface':
        """
        Создать новый экземпляр с указанным фрагментом.

        Аргументы:
            fragment: Новый фрагмент (без ведущего "#")

        Возвращает:
            UriInterface: Новый экземпляр с измененным фрагментом
        """
        pass

    @abstractmethod
    def __str__(self) -> str:
        """
        Возвращает строковое представление URI.

        Собирает все компоненты URI в соответствии с RFC 3986 Section 4.1.
        """
        pass
