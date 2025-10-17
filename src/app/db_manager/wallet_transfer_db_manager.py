from decimal import Decimal

from app.db_manager.wallet_transfer_db_manager_abstarct import WalletTransferDBManagerABC
from app.db_manager.db_connection import DBManagerBase
from app.db_manager.tables import VerifyCode, UserTable, Accounts, Transfers, TxStatus
from sqlalchemy import select, update, text
from sqlalchemy.dialects.postgresql import insert

from app.domain.user import User
from app.exception import UserNotFoundError
import typing as t

class WalletTransferDBManager(DBManagerBase, WalletTransferDBManagerABC):

    async def get_user_by_phone_number(self, phone_number: str = None):
        async with self.engine.begin() as connection:
            query = (
                select(UserTable.c.id.label("user_id"), UserTable.c.phone_number, VerifyCode)
                .join(VerifyCode, VerifyCode.c.phone_number == UserTable.c.phone_number)
            )
            if phone_number:
                query = query.where(UserTable.c.phone_number == phone_number)
            query = query.order_by(VerifyCode.c.created_at.desc()).limit(1)
            result = await connection.execute(query)
            row = result.mappings().one_or_none()

            if row is None:
                raise UserNotFoundError(message="Пользователь не найден")

            data = {
                "user_id": str(row["user_id"]),
                "phone_number": row["phone_number"],
                "sms_verification": {
                    "id": str(row["id"]),
                    "phone_number": row["phone_number"],
                    "code_hash": row["code"],
                    "confirmed_client_code": row["confirmed_client_code"],
                    "confirm_code": row["confirm_code"],
                    "attempt_count": row["attempt_count"],
                    "created_at": str(row["created_at"]),
                    "updated_at": str(row["updated_at"]) if row["updated_at"] is not None else None,
                }
            }

            return data

    async def save_user_state(self, user: User) -> t.Dict:
        async with self.engine.begin() as connection:
            query = insert(UserTable)
            query = query.values(id=user.user_id)
            query = query.values(phone_number=user.phone_number)
            query = query.on_conflict_do_nothing(index_elements=["id"])
            await connection.execute(query)
            if user.sms_verifications:
                for sms_verifications in user.sms_verifications:
                    query = insert(VerifyCode)
                    query = query.values(id=sms_verifications.sms_verification_id)
                    query = query.values(phone_number=sms_verifications.phone_number)
                    query = query.values(code=sms_verifications.code_hash)
                    query = query.values(confirmed_client_code=sms_verifications.confirmed_client_code)
                    query = query.values(confirm_code=sms_verifications.confirm_code)
                    query = query.values(attempt_count=sms_verifications.attempt_count)
                    query = query.on_conflict_do_update(
                        index_elements=["id"],
                        set_={
                            "confirmed_client_code": sms_verifications.confirmed_client_code,
                            "confirm_code": sms_verifications.confirm_code,
                            "attempt_count": sms_verifications.attempt_count
                        }
                    )
                    await connection.execute(query)
            return {"user_id": str(user.user_id), "phone_number": user.phone_number,
                    "sms_verification_id": str(sms_verifications.sms_verification_id)}

    async def create_account(self, user_id, currency, initial_balance=0):
        async with self.engine.begin() as connection:
            stmt = insert(Accounts).values(
                user_id=user_id,
                currency=currency,
                balance=initial_balance
            ).returning(
                    Accounts.c.id,
                    Accounts.c.currency,
                    Accounts.c.balance
                )
            result = await connection.execute(stmt)
            await connection.commit()
            return result.mappings().first()

    async def get_account_by_id(self, account_id):
        async with self.engine.begin() as connection:
            stmt = select(
                Accounts.c.id,
                Accounts.c.user_id,
                Accounts.c.currency,
                Accounts.c.balance,
                Accounts.c.is_active
            ).where(Accounts.c.id == account_id)

            result = await connection.execute(stmt)
            return result.mappings().first()

    async def create_transfer_atomic(
            self,
            from_acc_id,
            to_acc_id,
            source_amount: Decimal,
            target_amount: Decimal,
            rate_used: Decimal,
            fee_fixed: Decimal,
            fee_percent: Decimal,
            fee_amount: Decimal,
            idem_key: str | None,
    ):
        async with self.engine.begin() as connection:
            # блокируем строки (FOR UPDATE)
            await connection.execute(
                select(Accounts.c.id).where(Accounts.c.id == from_acc_id).with_for_update()
            )
            await connection.execute(
                select(Accounts.c.id).where(Accounts.c.id == to_acc_id).with_for_update()
            )

            # получаем баланс исходного счёта
            src_res = await connection.execute(
                select(Accounts.c.balance).where(Accounts.c.id == from_acc_id)
            )
            src_balance = Decimal(str(src_res.scalar_one()))

            if src_balance < source_amount:
                raise ValueError("Insufficient funds")

            # обновляем балансы
            await connection.execute(
                update(Accounts)
                .where(Accounts.c.id == from_acc_id)
                .values(balance=src_balance - source_amount)
            )

            dst_res = await connection.execute(
                select(Accounts.c.balance).where(Accounts.c.id == to_acc_id)
            )
            dst_balance = Decimal(str(dst_res.scalar_one()))

            await connection.execute(
                update(Accounts)
                .where(Accounts.c.id == to_acc_id)
                .values(balance=dst_balance + target_amount)
            )

            # создаём запись о переводе
            stmt = (
                insert(Transfers)
                .values(
                    from_account_id=from_acc_id,
                    to_account_id=to_acc_id,
                    source_amount=source_amount,
                    target_amount=target_amount,
                    rate_used=rate_used,
                    fee_fixed=fee_fixed,
                    fee_percent=fee_percent,
                    fee_amount=fee_amount,
                    status=TxStatus.completed,
                    idempotency_key=idem_key,
                )
                .returning(
                    Transfers.c.id,
                    Transfers.c.from_account_id,
                    Transfers.c.to_account_id,
                    Transfers.c.source_amount,
                    Transfers.c.target_amount,
                    Transfers.c.rate_used,
                    Transfers.c.fee_amount,
                    Transfers.c.status,
                )
            )

            result = await connection.execute(stmt)
            await connection.commit()

            return result.mappings().first()