from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from .request import RequestInterface
from .file import UploadedFileInterface


class ServerRequestInterface(RequestInterface, ABC):
    """
    Интерфейс для входящего HTTP-запроса на стороне сервера.

    Наследует RequestInterface и добавляет функциональность для работы с:
    - Параметрами сервера ($_SERVER)
    - Куками ($_COOKIE)
    - Параметрами запроса ($_GET)
    - Загруженными файлами ($_FILES)
    - Парсированным телом запроса ($_POST)
    - Атрибутами запроса

    Запросы считаются неизменяемыми - методы with_* возвращают новые экземпляры.
    """

    @abstractmethod
    def get_server_params(self) -> Dict[str, Any]:
        """
        Получает параметры сервера (аналог $_SERVER в PHP).

        Возвращает:
            Dict[str, Any]: Параметры сервера
        """
        pass

    @abstractmethod
    def get_cookie_params(self) -> Dict[str, str]:
        """
        Получает куки запроса (аналог $_COOKIE в PHP).

        Возвращает:
            Dict[str, str]: Словарь с куками
        """
        pass

    @abstractmethod
    def with_cookie_params(self, cookies: Dict[str, str]) -> 'ServerRequestInterface':
        """
        Создает копию запроса с указанными куками.

        Аргументы:
            cookies: Новые значения cookies (совместимые с форматом $_COOKIE)

        Возвращает:
            ServerRequestInterface: Новый экземпляр с измененными куками
        """
        pass

    @abstractmethod
    def get_query_params(self) -> Dict[str, Any]:
        """
        Получает параметры строки запроса (аналог $_GET в PHP).

        Возвращает:
            Dict[str, Any]: Параметры запроса
        """
        pass

    @abstractmethod
    def with_query_params(self, query: Dict[str, Any]) -> 'ServerRequestInterface':
        """
        Создает копию запроса с указанными параметрами запроса.

        Аргументы:
            query: Новые параметры запроса (совместимые с parse_str() в PHP)

        Возвращает:
            ServerRequestInterface: Новый экземпляр с измененными параметрами запроса
        """
        pass

    @abstractmethod
    def get_uploaded_files(self) -> Dict[str, Union[UploadedFileInterface, List[UploadedFileInterface]]]:
        """
        Получает загруженные файлы (аналог $_FILES в PHP).

        Возвращает:
            Dict[str, Union[UploadedFileInterface, List[UploadedFileInterface]]:
                Загруженные файлы в нормализованном виде
        """
        pass

    @abstractmethod
    def with_uploaded_files(self,
        uploaded_files: Dict[str, Union[UploadedFileInterface, List[UploadedFileInterface]]]
        ) -> 'ServerRequestInterface':
        """
        Создает копию запроса с указанными загруженными файлами.

        Аргументы:
            uploaded_files: Новые загруженные файлы

        Возвращает:
            ServerRequestInterface: Новый экземпляр с измененными файлами

        Исключения:
            ValueError: При неверной структуре uploaded_files
        """
        pass

    @abstractmethod
    def get_parsed_body(self) -> Optional[Union[Dict[str, Any], List[Any]]]:
        """
        Получает парсированное тело запроса (аналог $_POST в PHP).

        Для application/x-www-form-urlencoded или multipart/form-data с методом POST
        должен возвращать содержимое $_POST.

        Возвращает:
          Optional[Union[Dict[str, Any], List[Any]]:
              Парсированное тело запроса или None, если тело отсутствует
        """
        pass

    @abstractmethod
    def with_parsed_body(self, data: Optional[Union[Dict[str, Any], List[Any]]]) -> 'ServerRequestInterface':
        """
        Создает копию запроса с указанным парсированным телом.

        Аргументы:
            data: Новые парсированные данные (только dict, list или None)

        Возвращает:
            ServerRequestInterface: Новый экземпляр с измененным телом

        Исключения:
            ValueError: При неверном типе данных
        """
        pass

    @abstractmethod
    def get_attributes(self) -> Dict[str, Any]:
        """
        Получает атрибуты запроса.

        Атрибуты могут использоваться для хранения дополнительных параметров,
        полученных из запроса (результаты сопоставления пути, десериализованные
        данные и т.д.).

        Возвращает:
            Dict[str, Any]: Атрибуты запроса
        """
        pass

    @abstractmethod
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """
        Получает один атрибут запроса.

        Аргументы:
            name: Имя атрибута
            default: Значение по умолчанию, если атрибут не найден

        Возвращает:
            Any: Значение атрибута или default, если атрибут не найден
        """
        pass

    @abstractmethod
    def with_attribute(self, name: str, value: Any) -> 'ServerRequestInterface':
        """
        Создает копию запроса с указанным атрибутом.

        Аргументы:
            name: Имя атрибута
            value: Значение атрибута

        Возвращает:
            ServerRequestInterface: Новый экземпляр с измененным атрибутом
        """
        pass

    @abstractmethod
    def without_attribute(self, name: str) -> 'ServerRequestInterface':
        """
        Создает копию запроса без указанного атрибута.

        Аргументы:
            name: Имя удаляемого атрибута

        Возвращает:
            ServerRequestInterface: Новый экземпляр без указанного атрибута
        """
        pass
