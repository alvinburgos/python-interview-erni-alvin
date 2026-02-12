from models import Rate, Transaction, Currency
from db import get_engine
from sqlalchemy.orm import Session
from sqlalchemy import select

import requests
from datetime import date

# engine = get_engine()
# with Session(engine) as session:
#     rows = session.execute(select(Currency)).all()
#     for row in rows:
#         currency = row[0]
#         print(currency.id, currency.iso)
#     # print(len(rows))


# payload = {
#     "rate_date": "2026-02-01",
#     "base_currency": "PHP",
#     "quote_currency": "USD",
#     "side": "SELL",
#     "rate": "2.0",
# }

# resp = requests.post()

# url = "http://localhost:8000/rates"
# payload = {
#     "rate_date": date(2026, 2, 2).isoformat(),  # or use a specific date: "2024-01-15"
#     "base_currency": "PHP",
#     "quote_currency": "USD",
#     "side": "SELL",
#     "rate": "0.25"
# }

url = "http://localhost:8000/transaction"
payload = {
    "timestamp": "2026-02-02T10:30:00",
    "base_currency": "PHP",
    "quote_currency": "USD",
    "side": "SELL",
    "foreign_amount": "4.1234"
}



resp = requests.post(
    url,
    json=payload,
    headers={"Content-Type": "application/json"},
)


print(resp.content)
