from app.actions import (

    action_create_sms, action_verify_sms, action_create_account, action_create_transfer)
from app.db_manager.wallet_transfer_db_manager import WalletTransferDBManager as DBManager
from fastapi import Request, HTTPException, BackgroundTasks

from app.decode_auth_header import decode_auth_header
from app.schemas import VerifyCodeEvent, TransferCreate, AccountCreate, SendSmsRequest


async def read_root():
    return {"ver": "0.0.1"}


async def send_sms_user(data: SendSmsRequest):
    data = data.model_dump()
    phone_number = data.get("phone_number", "").lstrip("+")
    if not phone_number:
        raise HTTPException(status_code=400, detail="Phone number is required")

    return await action_create_sms(phone_number=phone_number, db_manager=DBManager())


async def verify_code(event: VerifyCodeEvent, request: Request):
    phone_number = event.phone_number.lstrip("+")

    event.phone_number = phone_number
    return await action_verify_sms(event, db_manager=DBManager())



async def create_account(data: AccountCreate, request: Request):
    auth_header = request.headers.get("Authorization")
    user_id = decode_auth_header(auth_header)
    data = data.model_dump()
    currency = data.get("currency")
    initial_balance = data.get("initial_balance", 0)

    return await action_create_account(
        user_id=user_id,
        currency=currency,
        initial_balance=initial_balance,
        db_manager=DBManager()
    )

async def create_transfer(data: TransferCreate, request: Request, background_tasks: BackgroundTasks):
    """
    Обработчик API для перевода между счетами.
    """
    auth_header = request.headers.get("Authorization")
    user_id = decode_auth_header(auth_header)

    return await action_create_transfer(
        user_id=user_id,
        data=data.model_dump(),
        db_manager=DBManager(),
        background_tasks=background_tasks
    )
