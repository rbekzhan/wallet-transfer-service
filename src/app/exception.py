class CustomBaseException(Exception):
    def __init__(self, status_code: int, message: str = None):
        self._status_code = status_code
        self._message = message or self.__class__.__name__
        super().__init__(self._message, self._status_code)

    @property
    def message(self) -> str:
        return self._message

    @property
    def status_code(self) -> int:
        return self._status_code

    def __str__(self) -> str:
        return self.__class__.__name__

class UserNotFoundError(CustomBaseException):
    def __init__(self, status_code: int = None, message: str = None):
        self._status_code = status_code or 404
        self._message = message or self.__class__.__name__
        super().__init__(self._status_code, self._message)

class TooManyTries(CustomBaseException):
    def __init__(self, code: int, status_code: int = None, message: str = None):
        self._status_code = status_code or 429
        self._code = code
        self._message = message or self.__class__.__name__
        super().__init__(self._status_code, self._message)

    @property
    def code(self) -> int:
        return self._code


class SMSCodeWasActivated(CustomBaseException):
    def __init__(self, code: int, status_code: int = None, message: str = None):
        self._status_code = status_code or 400
        self._code = code
        self._message = message or self.__class__.__name__
        super().__init__(self._status_code, self._message)

    @property
    def code(self) -> int:
        return self._code

class SMSCodeExpired(CustomBaseException):
    def __init__(self, code: int, status_code: int = None, message: str = None):
        self._status_code = status_code or 403
        self._code = code
        self._message = message or self.__class__.__name__
        super().__init__(self._status_code, self._message)

    @property
    def code(self) -> int:
        return self._code


class InvalidTokenError(CustomBaseException):
    def __init__(self, code: int, status_code: int = None, message: str = None):
        self._status_code = status_code or 401
        self._code = code
        self._message = message or self.__class__.__name__
        super().__init__(self._status_code, self._message)

    @property
    def code(self) -> int:
        return self._code

class ExpiredSignatureError(CustomBaseException):
    def __init__(self, code: int, status_code: int = None, message: str = None):
        self._status_code = status_code or 401
        self._code = code
        self._message = message or self.__class__.__name__
        super().__init__(self._status_code, self._message)

    @property
    def code(self) -> int:
        return self._code

class NotCorrectCode(CustomBaseException):
    def __init__(self, code: int, status_code: int = None, message: str = None):
        self._status_code = status_code or 404
        self._code = code
        self._message = message or self.__class__.__name__
        super().__init__(self._status_code, self._message)

    @property
    def code(self) -> int:
        return self._code