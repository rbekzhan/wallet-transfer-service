from pydantic import BaseModel, UUID4, Field, condecimal, constr
from typing import Optional

class VerifyCodeEvent:
    def __init__(self, code: str, phone_number: str):
        self.code = code
        self.phone_number = phone_number

class SmsRequest(BaseModel):
    phone_number: str


class VerifyCodeEvent(BaseModel):
    phone_number: str
    code: str



class TransferCreate(BaseModel):
    """Схема запроса для перевода между счетами"""
    from_account_id: UUID4 = Field(..., description="ID счёта, с которого списываются средства")
    to_account_id: UUID4 = Field(..., description="ID счёта, на который зачисляются средства")
    source_amount: Optional[condecimal(gt=0, max_digits=18, decimal_places=4)] = Field(
        None, description="Сумма списания в валюте исходного счёта"
    )
    target_amount: Optional[condecimal(gt=0, max_digits=18, decimal_places=4)] = Field(
        None, description="Сумма зачисления в валюте целевого счёта"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "from_account_id": "490d28cb-01bf-4179-b0ba-2dcc7927f02e",
                "to_account_id": "7d490c7b-0d27-47a3-8267-e049879fd693",
                "source_amount": 10.0
            }
        }


class AccountCreate(BaseModel):
    """Схема запроса для создания нового счёта"""
    currency: constr(min_length=3, max_length=3, to_upper=True) = Field(
        ..., description="Код валюты счёта (например, USD, KZT, EUR)"
    )
    initial_balance: condecimal(ge=0, max_digits=18, decimal_places=4) = Field(
        0, description="Начальный баланс счёта"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "currency": "USD",
                "initial_balance": 10000.0
            }
        }