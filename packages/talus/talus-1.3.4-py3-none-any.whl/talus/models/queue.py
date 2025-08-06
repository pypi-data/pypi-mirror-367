"""Queue model."""
from pydantic import BaseModel


class Queue(BaseModel):
    """
    Queue model.
    >>> from talus.models.queue import Queue
    >>> queue = Queue(name="my.queue")
    """

    name: str
    passive: bool = False
    durable: bool = True
    auto_delete: bool = False
    exclusive: bool = False
    arguments: dict | None = None

    def __str__(self):
        return self.name
