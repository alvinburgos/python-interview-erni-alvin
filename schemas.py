import enum
from datetime import date, datetime

# from pydantic import BaseModel
from decimal import Decimal
from typing import (
    Optional,
)

from pydantic import (
    BaseModel,
    Field,
)


class SideEnum(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"



def make_currency_iso_field():
    return Field(pattern=r"[A-Z]{3}")


def make_currency_value_field(nullable: bool = False):
    if nullable:
        return Field(max_digits=20, decimal_places=10, gt=Decimal(0), default=None)
    else:
        return Field(max_digits=20, decimal_places=10, gt=Decimal(0))


class RateCreate(BaseModel):
    rate_date: date
    base_currency: str = make_currency_iso_field()
    quote_currency: str = make_currency_iso_field()
    side: SideEnum
    rate: Optional[Decimal] = make_currency_value_field()


class TransactionCreate(BaseModel):
    _transaction_id: str | None = None

    timestamp: datetime
    base_currency: str = make_currency_iso_field()
    quote_currency: str = make_currency_iso_field()
    side: SideEnum
    base_amount: Optional[Decimal] = make_currency_value_field(nullable=True)
    foreign_amount: Optional[Decimal] = make_currency_value_field(nullable=True)

    def model_post_init(self, ctx):
        print("post init????", self.base_amount, self.foreign_amount)
        if (self.base_amount is None) == (self.foreign_amount is None):
            raise ValueError(
                "Exactly one of `base_amount` and `foreign_amount` must be set."
            )
