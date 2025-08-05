from abc import ABC
from collections.abc import Awaitable
from typing import Any, Self

from xproject.xcall import call_method


class CreateInstanceMixin(ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._is_closed: bool | None = None

    @classmethod
    def create_instance(cls, *args: Any, **kwargs: Any) -> Self | Awaitable[Self]:
        return cls(*args, **kwargs)

    def open(self) -> None:
        if self.is_closed:
            call_method(method=self._open)
        self._is_closed = False

    def _open(self) -> None:
        pass

    def close(self) -> None:
        if not self.is_closed:
            call_method(method=self._close)
        self._is_closed = True

    def _close(self) -> None:
        pass

    @property
    def is_closed(self) -> bool:
        return True if self._is_closed is True or self._is_closed is None else False
