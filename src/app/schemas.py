from pydantic import BaseModel


class VerifyCodeEvent:
    def __init__(self, code: str, phone_number: str):
        self.code = code
        self.phone_number = phone_number

class SmsRequest(BaseModel):
    phone_number: str


class VerifyCodeEvent(BaseModel):
    phone_number: str
    code: str