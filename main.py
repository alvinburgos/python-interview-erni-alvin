from datetime import date
# from pydantic import BaseModel
from decimal import (
    Decimal,
    ROUND_DOWN,
)
from fastapi import FastAPI, HTTPException
from sqlalchemy import (
    select,
)
from sqlalchemy.orm import (
    Session,
)
from models import (
    Currency, Rate, Transaction
)
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
)
from schemas import RateCreate, SideEnum, TransactionCreate
from db import get_engine
import dataclasses

app = FastAPI()

# transactions = []
rates = [
    RateCreate(
        rate_date=date(2026, 1, 1),
        base_currency="PHP",
        quote_currency="USD",
        side=SideEnum.SELL,
        rate=Decimal("1.12"),
    ),
    RateCreate(
        rate_date=date(2026, 1, 1),
        base_currency="PHP",
        quote_currency="USD",
        side=SideEnum.BUY,
        rate=Decimal("2.13"),
    ),
]

# transactions = [
#     TransactionCreate(base_currency="PHP", quote_currency="USD", side=SideEnum.SELL, timestamp=datetime(2026, 1, 1), base_amount=Decimal("1.012345"), foreign_amount=Decimal("2")),
# ]

# print(transactions)




@app.get("/rates")
def get_rates():
    with Session(get_engine()) as session:
        result = session.execute(select(Rate)).all()
    return [row[0] for row in result]


@app.post("/rates")
def update_rates(rate_create: RateCreate):
    # todo: validation
    with Session(get_engine()) as session:
        isos = (rate_create.base_currency, rate_create.quote_currency)
        iso_to_currency = Currency.get_currencies_from_isos(isos)
        for iso in isos:
            if iso not in iso_to_currency:
                raise HTTPException(422, f"Currency '{iso}' does not exist in the database.")
        rate_dump = rate_create.model_dump()
        rate_dump["base_currency_id"] = iso_to_currency[rate_dump.pop("base_currency")].id
        rate_dump["quote_currency_id"] = iso_to_currency[rate_dump.pop("quote_currency")].id
        try:
            session.add(Rate(**rate_dump))
            session.commit()
        except IntegrityError as e:
            raise HTTPException(422, detail={"error": 422, "message": "rate, side, base and quote currency should be unique collectively"})
            
    return {}

@app.get("/transaction")
def get_transactions():
    with Session(get_engine()) as session:
        result = session.execute(select(Rate)).all()
    return [row[0] for row in result]

@app.post("/transaction")
def create_transaction(tc: TransactionCreate):
    if (tc.base_amount is None) == (tc.foreign_amount is None):
        raise HTTPException(
            status_code=422, 
            detail={"error": "You must specify only one of 'base_amount' and 'foreign_amount'"},
        )
    with Session(get_engine()) as session:
        query = select(Rate).where(
            Rate.rate_date == tc.timestamp.date(),
            select(1).where(
                Rate.base_currency_id == Currency.id,
                Currency.iso == tc.base_currency,
            ).exists(),
            select(1).where(
                Rate.quote_currency_id == Currency.id,
                Currency.iso == tc.quote_currency,
            ).exists(),
            Rate.side == tc.side,
        )
        try:
            rate = session.execute(query).one().tuple()[0]
        except NoResultFound:
            raise HTTPException(status_code=422, detail={"error": "No rate available"})
        
        data = tc.model_dump()
        if tc.foreign_amount is not None:
            data["base_amount"] = tc.foreign_amount / rate.rate
        elif tc.base_amount is not None:
            data["foreign_amount"] = tc.base_amount * rate.rate
        data["rounded_version"] = data["foreign_amount"].quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        data["rounding_adjustment"] = data["foreign_amount"] - data["rounded_version"]
        data["foreign_amount"] = data.pop("rounded_version")
        data["rate_used_id"] = rate.id
        data.pop("base_currency")
        data.pop("quote_currency")
        data.pop("side")
        transaction = Transaction(**data)
        session.add(transaction)
        session.commit()
        transaction_dump = dataclasses.asdict(transaction)
        transaction_dump["base_currency"] = tc.base_currency
        transaction_dump["quote_currency"] = tc.quote_currency
        transaction_dump["side"] = tc.side
        transaction_dump["effective_rate"] = rate.rate
        transaction_dump["fee_amount"] = 0.0
        transaction_dump.pop("rate_used")
        return transaction_dump
        