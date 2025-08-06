"""Exchange models."""
from pika.exchange_type import ExchangeType
from pydantic import BaseModel


class Exchange(BaseModel):
    """
    Exchange model.

    >>> from talus.models.exchange import Exchange
    >>> exchange = Exchange(name="my.exchange")
    """

    name: str = "default.x"
    type: ExchangeType = ExchangeType.direct
    passive: bool = False
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: dict | None = None

    def __str__(self):
        return self.name
