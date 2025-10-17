import typing as t
from abc import ABC, abstractmethod
from decimal import Decimal

from app.domain.user import User


class WalletTransferDBManagerABC(ABC):
    @abstractmethod
    async def save_user_state(self, user: User) -> t.Dict:
        raise NotImplementedError("The method must be implemented")

    @abstractmethod
    async def get_user_by_phone_number(self,  phone_number: str) -> t.Dict:
        raise NotImplementedError("The method must be implemented")

    @abstractmethod
    async def create_account(self, user_id: str, currency: str, initial_balance: float) -> t.Dict:
        raise NotImplementedError("The method must be implemented")

    @abstractmethod
    async def create_transfer_atomic(self, from_acc_id,
            to_acc_id,
            source_amount: Decimal,
            target_amount: Decimal,
            rate_used: Decimal,
            fee_fixed: Decimal,
            fee_percent: Decimal,
            fee_amount: Decimal,
            idem_key: str | None,):
        raise NotImplementedError("The method must be implemented")

    @abstractmethod
    async def get_account_by_id(self, account_id: str) -> t.Dict:
        raise NotImplementedError("The method must be implemented")