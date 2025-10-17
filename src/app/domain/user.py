import typing as t

from uuid import uuid4
from app.domain.sms_confirmation import SMSVerification


class User:

    def __init__(
            self,
            user_id: str = None,
            phone_number: str = None,
            tag: str = None,
            sms_verifications: t.List[SMSVerification] = None,
    ):
        self._user_id = user_id or uuid4()
        self._phone_number = phone_number
        self._tag = tag
        self._sms_verifications = sms_verifications or []

    @property
    def phone_number(self) -> str:
        return self._phone_number

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def tag(self) -> str:
        return self._tag

    @property
    def sms_verifications(self) -> t.List[SMSVerification]:
        return self._sms_verifications

    def add_sms_verification(self, sms_verification: SMSVerification) -> None:
        self._sms_verifications.append(sms_verification)


