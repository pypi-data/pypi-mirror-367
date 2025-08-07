from pathlib import Path
from types import TracebackType
from typing import final

from _typeshed import StrPath
from typing_extensions import Self

__all__ = ("AtomicWriter",)

@final
class AtomicWriter:
    __slots__ = ("_impl",)

    def __init__(self, destination: StrPath, *, overwrite: bool = False) -> None: ...
    @property
    def destination(self) -> Path: ...
    @property
    def overwrite(self) -> bool: ...
    def write_bytes(self, data: bytes, /) -> None: ...
    def write_text(self, data: str, /) -> None: ...
    def commit(self) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None: ...
