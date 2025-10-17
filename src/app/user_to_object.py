import typing as t
from datetime import datetime

from app.domain.sms_confirmation import SMSVerification
from app.domain.user import User


async def sms_verification_to_object(sms: t.Dict) -> SMSVerification:
    sms_verification = SMSVerification(
        sms_verification_id=str(sms["id"]),
        phone_number=sms["phone_number"],
        code_hash=sms["code_hash"],
        confirm_code=sms["confirm_code"],
        attempt_count=sms["attempt_count"],
        created_at=datetime.strptime(sms["created_at"], '%Y-%m-%d %H:%M:%S.%f'),
        updated_at=datetime.strptime(
            sms["updated_at"], '%Y-%m-%d %H:%M:%S.%f'
        ) if sms["updated_at"] is not None else None
    )
    return sms_verification


async def user_to_object(user: t.Dict) -> User:
    user_obj = User(
        user_id=str(user["user_id"]),
        phone_number=str(user["phone_number"]),
        # Преобразуем словарь sms_verification в объект SMSVerification
        sms_verifications=[await sms_verification_to_object(user["sms_verification"])]
    )
    return user_obj
