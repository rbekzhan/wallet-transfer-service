import typing
from decimal import Decimal

import jwt
import uuid

from fastapi import HTTPException, BackgroundTasks

from app.db_manager.rabbit.producer import publish_event
from app.db_manager.tables import TxStatus
from app.fees import calc_fee, get_fee
from app.rates_mock import RateServiceMock
from app.schemas import VerifyCodeEvent as Event
from app.db_manager.wallet_transfer_db_manager_abstarct import WalletTransferDBManagerABC as DBManager
from datetime import timedelta, datetime
from app.db_manager.redis_tools import RedisConnection as Redis
from app.config import SMS_SERVICE, SECRET_KEY
from app.domain.sms_confirmation import SMSVerification
from app.domain.user import User
from app.exception import InvalidTokenError, ExpiredSignatureError, UserNotFoundError, NotCorrectCode
from app.user_to_object import user_to_object


def generate_tokens(user_id):
    session_id = str(uuid.uuid4())  # создаем уникальный идентификатор сессии
    access_token = jwt.encode(
        {
            "user_id": user_id,
            "session_id": session_id,  # добавляем session_id
            "exp": datetime.utcnow() + timedelta(minutes=15)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    refresh_token = jwt.encode(
        {
            "user_id": user_id,
            "session_id": session_id,  # добавляем session_id
            "exp": datetime.utcnow() + timedelta(days=30)
        },
        SECRET_KEY,
        algorithm="HS256"
    )

    store_session_in_redis(user_id, session_id, refresh_token)
    return {"access_token": access_token, "refresh_token": refresh_token}


def store_session_in_redis(user_id, session_id, refresh_token):
    # Сохраняем session_id и refresh_token, привязанные к user_id
    session_key = f"session:{user_id}"
    with Redis() as client:
        client.hset(session_key, "session_id", session_id)
        client.hset(session_key, "refresh_token", refresh_token)


async def is_session_valid(user_id, session_id):
    # Проверяем, совпадает ли session_id из токена с тем, что хранится в Redis
    session_key = f"session:{user_id}"
    with Redis() as client:
        stored_session_id = client.hget(session_key, "session_id")
    return stored_session_id.decode("utf-8") == session_id if stored_session_id else False


async def action_refresh_token(token):
    try:
        decoded_refresh_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_refresh_token.get("user_id")
        session_id = decoded_refresh_token.get("session_id")

        if not await is_session_valid(user_id, session_id):
            raise InvalidTokenError(message="Session is invalid, please sign in again", code=11)

        new_tokens = generate_tokens(user_id)
        return new_tokens

    except jwt.ExpiredSignatureError:
        raise ExpiredSignatureError(message="Token expired", code=6)


async def action_create_sms(phone_number: str, db_manager: DBManager):
    try:
        user_data = await db_manager.get_user_by_phone_number(phone_number=phone_number)
        user: User = await user_to_object(user=user_data)
        sms_verification: SMSVerification = user.sms_verifications[0]
        if not False and sms_verification:
            sms_verification.check()
    except UserNotFoundError:
        user = User(phone_number=phone_number)

    sms_verification = SMSVerification(phone_number=phone_number)
    await sms_verification.create_sms_message()
    user.add_sms_verification(sms_verification=sms_verification)
    try:
        await db_manager.save_user_state(user=user)
        # if SMS_SERVICE == "PROD":
            # sms = TOOSMSCKZ()
            # asyncio.create_task(sms.send_sms(phone_number=phone_number, message=sms_verification.message))
        return {"sms_verification_id": str(sms_verification.sms_verification_id)}
    except Exception as e:
        raise ValueError(e)


async def action_verify_sms(event: Event, db_manager: DBManager):
    user_data = await db_manager.get_user_by_phone_number(phone_number=event.phone_number)
    user: User = await user_to_object(user=user_data)
    sms_confirmation: SMSVerification = user.sms_verifications[0]
    is_confirmed: bool = sms_confirmation.confirm_sms_code(code=event.code)
    user.add_sms_verification(sms_verification=sms_confirmation)
    await db_manager.save_user_state(user=user)

    if is_confirmed is False:
        raise NotCorrectCode(message="Неверный код подтверждения", code=2)

    tokens: typing.Dict = generate_tokens(user_id=user.user_id)
    return tokens


async def action_logout_token(token, user_id):
    decoded_access_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    session_id = decoded_access_token.get("session_id")
    refresh_key = f"session:{user_id}"

    with Redis() as client:
        stored_session_id = client.hget(refresh_key, "session_id")

        if stored_session_id and stored_session_id.decode("utf-8") == session_id:
            client.hdel(refresh_key, "session_id")
            client.hdel(refresh_key, "refresh_token")

            client.sadd("blacklist_access_tokens", token)

            return {"message": "Logged out successfully"}

    raise ValueError("Session ID mismatch: User may already be logged out or using a different session.")


async def action_create_account(user_id, currency: str, initial_balance: float, db_manager: DBManager):
    """
    Создание нового счёта пользователю
    """
    if not currency:
        return {"error": "Currency is required"}

    account = await db_manager.create_account(
        user_id=user_id,
        currency=currency.upper(),
        initial_balance=initial_balance
    )
    return {"message": "Account created successfully", "account": account}


async def action_create_transfer(user_id, data: dict, db_manager: DBManager, background_tasks: BackgroundTasks):
    """
    Выполняет перевод между счетами с конвертацией и комиссией.
    """

    from_account_id = data.get("from_account_id")
    to_account_id = data.get("to_account_id")
    source_amount = data.get("source_amount")
    target_amount = data.get("target_amount")
    if not from_account_id or not to_account_id:
        raise HTTPException(status_code=400, detail="Both from_account_id and to_account_id are required")

    # Загрузка счетов
    src = await db_manager.get_account_by_id(from_account_id)
    dst = await db_manager.get_account_by_id(to_account_id)
    if not src or not dst:
        raise HTTPException(404, detail="Account not found")

    if str(src["user_id"]) != user_id:
        logger.warning(f"Account not found: from={from_account_id}, to={to_account_id}")
        raise HTTPException(403, detail="Cannot transfer from another user's account")

    if not src["is_active"] or not dst["is_active"]:
        raise HTTPException(400, detail="Account inactive")

    # курс валют (mock)
    rate_service = RateServiceMock()
    rate = await rate_service.get_rate(src["currency"], dst["currency"])

    # комиссия
    fee_fixed, fee_percent = get_fee(src["currency"], dst["currency"])

    # Расчёт сумм
    if source_amount:
        source_amount = Decimal(str(source_amount))
        fee_amount = calc_fee(source_amount, fee_fixed, fee_percent)
        net_source = (source_amount - fee_amount).quantize(Decimal("0.0001"))

        # пересчитать в валюту назначения
        target_amount = (net_source * rate).quantize(Decimal("0.0001"))
    elif target_amount:
        target_amount = Decimal(str(target_amount))
        gross_source = (target_amount / rate).quantize(Decimal("0.0001"))
        fee_amount = calc_fee(gross_source, fee_fixed, fee_percent)
        source_amount = (gross_source + fee_amount).quantize(Decimal("0.0001"))

    else:
        raise HTTPException(422, detail="Provide either source_amount or target_amount")

    # Проверка баланса
    if Decimal(str(src["balance"])) < source_amount:
        raise HTTPException(400, detail="Insufficient funds")

    # атомарно
    try:
        transfer = await db_manager.create_transfer_atomic(
            from_acc_id=uuid.UUID(from_account_id),
            to_acc_id=uuid.UUID(to_account_id),
            source_amount=source_amount,
            target_amount=target_amount,
            rate_used=rate,
            fee_fixed=fee_fixed,
            fee_percent=fee_percent,
            fee_amount=fee_amount,
            idem_key=None,
        )

        background_tasks.add_task(
            publish_event,
            "transfer_completed",
            {
                "user_id": user_id,
                "from": str(from_account_id),
                "to": str(to_account_id),
                "amount": float(source_amount),
                "currency_from": src["currency"],
                "currency_to": dst["currency"],
                "target_amount": float(target_amount),
                "status": TxStatus.completed,
            },
        )

        return {
            "status": TxStatus.completed,
            "transfer": {
                "id": str(transfer["id"]),
                "from_account_id": transfer["from_account_id"],
                "to_account_id": transfer["to_account_id"],
                "source_amount": float(source_amount),
                "target_amount": float(target_amount),
                "rate_used": float(rate),
                "fee_amount": float(fee_amount),
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {e}")