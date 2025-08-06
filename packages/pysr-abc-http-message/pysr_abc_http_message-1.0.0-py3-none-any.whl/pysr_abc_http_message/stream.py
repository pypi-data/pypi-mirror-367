from abc import ABC, abstractmethod
from typing import Optional, Union, Any, IO
import io


class StreamInterface(ABC):
    """
        Интерфейс для работы с потоком данных.

        Обычно экземпляр будет оборачивать поток данных (например, файловый поток).
        Этот интерфейс предоставляет общие операции для работы с потоками, включая
        чтение всего потока в строку.
        """

    @abstractmethod
    def __str__(self) -> str:
        """
        Читает все данные из потока в строку, от начала до конца.

        Метод ДОЛЖЕН попытаться перейти в начало потока перед чтением
        и читать до конца потока.

        Внимание: Это может привести к загрузке большого объема данных в память.

        Возвращает:
            str: Содержимое потока в виде строки
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        Закрывает поток и все связанные ресурсы.
        """
        pass

    @abstractmethod
    def detach(self) -> Optional[IO[Any]]:
        """
        Отсоединяет базовый ресурс от потока.

        После отсоединения поток переходит в нерабочее состояние.

        Возвращает:
            Optional[IO]: Базовый поток Python, если существует, или None
        """
        pass

    @abstractmethod
    def get_size(self) -> Optional[int]:
        """
        Получает размер потока, если он известен.

        Возвращает:
            Optional[int]: Размер в байтах, если известен, или None
        """
        pass

    @abstractmethod
    def tell(self) -> int:
        """
        Возвращает текущую позицию указателя чтения/записи в потоке.

        Возвращает:
            int: Текущая позиция

        Исключения:
            RuntimeError: В случае ошибки
        """
        pass

    @abstractmethod
    def eof(self) -> bool:
        """
        Проверяет, достигнут ли конец потока.

        Возвращает:
            bool: True, если достигнут конец потока, иначе False
        """
        pass

    @abstractmethod
    def is_seekable(self) -> bool:
        """
        Проверяет, поддерживается ли произвольный доступ в потоке.

        Возвращает:
            bool: True, если поток поддерживает seek, иначе False
        """
        pass

    @abstractmethod
    def seek(self, offset: int, whence: int = io.SEEK_SET) -> None:
        """
        Перемещает указатель позиции в потоке.

        Аргументы:
            offset: Смещение
            whence: Откуда отсчитывать смещение:
                - io.SEEK_SET: от начала потока
                - io.SEEK_CUR: от текущей позиции
                - io.SEEK_END: от конца потока

        Исключения:
            RuntimeError: В случае ошибки
        """
        pass

    @abstractmethod
    def rewind(self) -> None:
        """
        Перемещает указатель в начало потока.

        Если поток не поддерживает seek, вызывает исключение.
        В противном случае эквивалентно seek(0).

        Исключения:
            RuntimeError: Если поток не поддерживает seek
        """
        pass

    @abstractmethod
    def is_writable(self) -> bool:
        """
        Проверяет, доступна ли запись в поток.

        Возвращает:
            bool: True, если запись возможна, иначе False
        """
        pass

    @abstractmethod
    def write(self, string: str) -> int:
        """
        Записывает данные в поток.

        Аргументы:
            string: Строка для записи

        Возвращает:
            int: Количество записанных байт

        Исключения:
            RuntimeError: В случае ошибки записи
        """
        pass

    @abstractmethod
    def is_readable(self) -> bool:
        """
        Проверяет, доступно ли чтение из потока.

        Возвращает:
            bool: True, если чтение возможно, иначе False
        """
        pass

    @abstractmethod
    def read(self, length: int) -> str:
        """
        Читает данные из потока.

        Аргументы:
            length: Максимальное количество байт для чтения

        Возвращает:
            str: Прочитанные данные. Может быть меньше length, если в потоке
                 недостаточно данных.

        Исключения:
            RuntimeError: В случае ошибки чтения
        """
        pass

    @abstractmethod
    def get_contents(self) -> str:
        """
        Читает все оставшиеся данные из потока в строку.

        Возвращает:
            str: Оставшиеся данные в потоке

        Исключения:
            RuntimeError: Если произошла ошибка при чтении
        """
        pass

    @abstractmethod
    def get_metadata(self, key: Optional[str] = None) -> Union[dict, Any, None]:
        """
        Получает метаданные потока или значение конкретного ключа метаданных.

        Ключи соответствуют возвращаемым Python-функцией stream.get_meta_data().

        Аргументы:
            key: Опциональный ключ для получения конкретного значения

        Возвращает:
            - Если key не указан: словарь со всеми метаданными
            - Если key указан: соответствующее значение или None, если ключ не найден
        """
        pass
