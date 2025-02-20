"""Module for getting exchange rates."""

from decimal import Decimal
from typing import Dict, List

import httpx
from pydantic import BaseModel, Field

from dundie.settings import API_BASE_URL


class USDRate(BaseModel):
    """Model for USD rate."""

    code: str = Field(default="USD")
    codein: str = Field(default="USD")
    name: str = Field(default="Dolar/Dolar")
    values: Decimal = Field(alias="high")


def get_rates(currencies: List[str]) -> Dict[str, USDRate]:
    """Gets current rate for USD vs Currency.

    Args:
        currencies (List[str]): List of currencies to get rate for.

    Returns:
        Dict[str, USDRate]: Dictionary of currency and rate.
    """
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
