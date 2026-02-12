from datetime import date, datetime
# from pydantic import BaseModel
from decimal import Decimal
from sqlalchemy import (
    Enum,
    ForeignKey,
    Numeric,
    String,
    select,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
    validates,
)
from typing import Iterable

from schemas import SideEnum
from db import get_engine
from dataclasses import dataclass
import uuid

class Base(DeclarativeBase):
    pass


class Currency(Base):
    __tablename__ = "currency"
    id: Mapped[int] = mapped_column(primary_key=True)
    iso: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)
    
    @classmethod
    def get_currencies_from_isos(cls, isos: Iterable[str]) -> dict[str, "Currency"]:
        with Session(get_engine()) as session:
            iso_to_currency = session.execute(
                select(Currency.iso, Currency).where(Currency.iso.in_(isos))
            ).all()
        return {iso: currency for iso, currency in iso_to_currency}
    
    def __repr__(self):
        return self.iso
        

class Rate(Base):
    __tablename__ = "rate"
    id: Mapped[int] = mapped_column(primary_key=True)
    rate_date: Mapped[date] = mapped_column(nullable=False)
    base_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id"), nullable=False
    )
    base_currency: Mapped[Currency] = relationship(foreign_keys=[base_currency_id])
    quote_currency_id: Mapped[int] = mapped_column(
        ForeignKey("currency.id"), nullable=False
    )
    quote_currency: Mapped[Currency] = relationship(foreign_keys=[quote_currency_id])

    side: Mapped[SideEnum] = mapped_column(Enum(SideEnum), nullable=False)
    rate: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )
    
    @validates("rate")
    def validate_positive_decimals(self, key, value):
        if value <= 0:
            raise ValueError("amount must be positive")
        return value

    __table_args__ = (
        UniqueConstraint("rate_date", "base_currency_id", "quote_currency_id", "side"),
    )
    
    def __repr__(self):
        return f"<Rate rate_date={self.rate_date} base_currency={self.base_currency.iso} quote_currency={self.quote_currency.iso} side={self.side}"
        
# @dataclass

@dataclass
class Transaction(Base):
    __tablename__ = "transaction"
    id: Mapped[str] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column()
    rate_used_id: Mapped[int] = mapped_column(ForeignKey("rate.id"))
    rate_used: Mapped[Rate] = relationship()
    base_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )
    foreign_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )
    rounding_adjustment: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=4), nullable=False
    )

    @validates("base_amount", "foreign_amount")
    def validate_positive_decimals(self, key, value):
        if value <= 0:
            raise ValueError("amount must be positive")
        return value

    def __init__(self, **kwargs):
        date = kwargs["timestamp"].date().isoformat()
        random = uuid.uuid4().hex[:8]
        kwargs["id"] = f"TXN-{date}-{random}"
        super().__init__(**kwargs)