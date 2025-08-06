from abc import ABC, abstractmethod
from typing import Optional
from .stream import StreamInterface


class UploadedFileInterface(ABC):
    """
    Объект-значение, представляющий файл, загруженный через HTTP-запрос.

    Экземпляры этого интерфейса считаются неизменяемыми - все методы, которые
    могут изменить состояние, должны возвращать новый экземпляр, сохраняя
    внутреннее состояние текущего.
    """

    @abstractmethod
    def get_stream(self) -> StreamInterface:
        """
        Получает поток для работы с загруженным файлом.

        Возвращает:
            StreamInterface: Поток, представляющий загруженный файл

        Исключения:
            RuntimeError: Если поток недоступен или не может быть создан,
                        или если метод move_to() уже был вызван ранее
        """
        pass

    @abstractmethod
    def move_to(self, target_path: str) -> None:
        """
        Перемещает загруженный файл в новое место.

        Этот метод является альтернативой move_uploaded_file() в PHP и должен
        работать как в SAPI, так и в не-SAPI окружениях.

        Исходный файл или поток ДОЛЖЕН быть удален после завершения операции.

        Аргументы:
            target_path: Путь для перемещения файла (может быть абсолютным или относительным)

        Исключения:
            ValueError: Если указан недопустимый target_path
            RuntimeError: При ошибке во время перемещения или при повторном вызове метода
        """
        pass

    @abstractmethod
    def get_size(self) -> Optional[int]:
        """
        Получает размер файла в байтах.

        Возвращает:
            Optional[int]: Размер файла в байтах или None, если неизвестен
        """
        pass

    @abstractmethod
    def get_error(self) -> int:
        """
        Получает код ошибки загрузки файла.

        Возвращает:
            int: Код ошибки (аналог PHP UPLOAD_ERR_XXX констант)

        При успешной загрузке должен возвращать 0 (UPLOAD_ERR_OK)
        """
        pass

    @abstractmethod
    def get_client_filename(self) -> Optional[str]:
        """
        Получает оригинальное имя файла, отправленное клиентом.

        Внимание: Не стоит доверять этому значению, так как клиент может
        отправить вредоносное имя файла.

        Возвращает:
            Optional[str]: Имя файла или None, если не предоставлено
        """
        pass

    @abstractmethod
    def get_client_media_type(self) -> Optional[str]:
        """
        Получает MIME-тип файла, отправленный клиентом.

        Внимание: Не стоит доверять этому значению, так как клиент может
        отправить вредоносный MIME-тип.

        Возвращает:
            Optional[str]: MIME-тип файла или None, если не предоставлен
        """
        pass
