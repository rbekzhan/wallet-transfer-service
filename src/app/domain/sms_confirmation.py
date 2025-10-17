from datetime import datetime, timedelta
from random import choice
from uuid import uuid4
from passlib.context import CryptContext

from app.config import SMS_LIFE_TIME, SMS_SERVICE
from app.exception import TooManyTries, SMSCodeWasActivated, SMSCodeExpired

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class SMSVerification:
    def __init__(
            self,
            sms_verification_id: str = None,
            phone_number: str = None,
            message: str = None,
            code_hash: str = None,
            confirm_code: bool = None,
            attempt_count: int = None,
            confirmed_client_code: str = None,
            created_at: datetime = None,
            updated_at: datetime = None,
    ):
        """
        :param phone: Номер телефона
        :param template: Текст смс
        :param reference: Ссылка на объект
        :param sent: Статус отправки
        :param code_hash: Хэш кода
        """

        self._sms_verification_id = sms_verification_id or uuid4()
        self._phone_number = phone_number
        self._message = message
        self._template = "kod: {code}"
        self._code_hash = code_hash
        self._created_at = created_at
        self._updated_at = updated_at
        self._attempt_count = attempt_count or 0
        self._confirm_code = confirm_code or False
        self._confirmed_client_code = confirmed_client_code
        self._life_time = SMS_LIFE_TIME

    @property
    def sms_verification_id(self) -> str:
        return self._sms_verification_id

    @property
    def phone_number(self) -> str:
        return self._phone_number

    @property
    def message(self) -> str:
        return self._message

    @property
    def template(self) -> str:
        return self._template

    @property
    def code_hash(self) -> str:
        return self._code_hash

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def confirm_code(self) -> bool:
        return self._confirm_code

    @property
    def confirmed_client_code(self) -> str:
        return self._confirmed_client_code

    @property
    def attempt_count(self) -> int:
        return self._attempt_count

    @property
    def is_sms_lifetime_status(self) -> bool:
        """ Статус жизни СМС """
        now = datetime.timestamp(datetime.utcnow())
        created_date = datetime.timestamp(self._created_at + timedelta(minutes=self._life_time))
        return now < created_date

    @property
    def is_life_sms_confirmation(self) -> bool:
        """ Проверка на количество попыток и жизненного цикла смс """
        if not self._confirm_code and (self._attempt_count >= 5 or not self.is_sms_lifetime_status):
            return False
        return True

    def check(self):
        if self.is_life_sms_confirmation and self.is_sms_lifetime_status and self.confirm_code is False:
            time_in_minutes = round(SMS_LIFE_TIME / 60)
            raise TooManyTries(
                message=f"Отправка сообщений на этот номер заблокирована попробуйте через {time_in_minutes} минут",
                code=1
            )

    async def create_sms_message(self) -> None:
        """ Формирование СМС """
        code = '1111'
        if SMS_SERVICE == "PROD":
            print('DDS')
            code = "".join([choice("1234567890") for _ in range(4)])

        self._message = self._template.format(code=code)
        self._code_hash = pwd_context.hash(code)
        self._created_at = datetime.utcnow()

    def confirm_sms_code(self, code) -> bool:
        """ Исключения проверки смс кода """
        if self._confirm_code:
            raise SMSCodeWasActivated(message="СМС код уже был активирован", code=1)
        if self._attempt_count >= 5:
            raise TooManyTries(message="Превышено количество попыток ввода кода подтверждения", code=3)
        if not self.is_sms_lifetime_status:
            raise SMSCodeExpired(message="СМС код устарел", code=5)
        self._attempt_count += 1
        if pwd_context.verify(code, self._code_hash):
            self._confirmed_client_code = code
            self._confirm_code = True
            return True
        return False
