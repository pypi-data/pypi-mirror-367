from abc import ABC, abstractmethod
from .message import MessageInterface


class ResponseInterface(MessageInterface, ABC):
    """
    Интерфейс для исходящего HTTP-ответа от сервера.

    Содержит свойства согласно HTTP-спецификации:
    - Версия протокола
    - Код состояния и поясняющая фраза
    - Заголовки
    - Тело сообщения

    Ответы считаются неизменяемыми - все методы, изменяющие состояние,
    должны возвращать новый экземпляр.
    """

    @abstractmethod
    def get_status_code(self) -> int:
        """
        Получает код состояния HTTP-ответа.

        Возвращает:
            int: 3-значный код состояния (например, 200, 404)
        """
        pass

    @abstractmethod
    def with_status(self, code: int, reason_phrase: str = '') -> 'ResponseInterface':
        """
        Создает копию ответа с указанным кодом состояния и поясняющей фразой.

        Если поясняющая фраза не указана, может использоваться фраза по умолчанию
        из RFC 7231 или реестра IANA.

        Аргументы:
            code: 3-значный код состояния
            reason_phrase: Поясняющая фраза (опционально)

        Возвращает:
            ResponseInterface: Новый экземпляр с измененным статусом

        Исключения:
            ValueError: При недопустимом коде состояния

        Ссылки:
            - RFC 7231, Section 6: https://tools.ietf.org/html/rfc7231#section-6
            - IANA HTTP Status Codes: https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
        """
        pass

    @abstractmethod
    def get_reason_phrase(self) -> str:
        """
        Получает поясняющую фразу для кода состояния.

        Если фраза не указана явно, может возвращать фразу по умолчанию
        из RFC 7231 или реестра IANA.

        Возвращает:
            str: Поясняющая фраза. Пустая строка, если фраза отсутствует.

        Ссылки:
            - RFC 7231, Section 6: https://tools.ietf.org/html/rfc7231#section-6
            - IANA HTTP Status Codes: https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
        """
        pass
