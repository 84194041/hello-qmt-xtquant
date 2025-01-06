from typing import Any

class HttpException(Exception):
    def __init__(self, isSuccess: bool, code: int, message: str = '', data: Any = None):
        self.isSuccess = isSuccess
        self.code = code
        self.message = message
        self.data = data
        self.status_code = code
