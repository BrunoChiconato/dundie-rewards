import httpx

from dundie.settings import API_BASE_URL
from typing import List, Dict
from pydantic import BaseModel, Field
from decimal import Decimal


class USDRate(BaseModel):
    code: str = Field(default="USD")
    codein: str = Field(default="USD")
    name: str = Field(default="Dolar/Dolar")
    values: Decimal = Field(alias="high")


def get_rates(currencies: List[str]) -> Dict[str, USDRate]:
    """Gets current rate for USD vs Currency"""
    return_data = {}
    for currency in currencies:
        if currency == "USD":
            return_data[currency] = USDRate(high=1)
        else:
            response = httpx.get(API_BASE_URL.format(currency=currency))
            if response.status_code == 200:
                data = response.json()[f"USD{currency}"]
                return_data[currency] = USDRate(**data)
            else:
                return_data[currency] = USDRate(name="Error", high=0)

    return return_data