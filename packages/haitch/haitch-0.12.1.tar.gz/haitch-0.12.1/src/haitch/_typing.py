from typing import Iterable, Literal, NewType, Protocol, Union, runtime_checkable

from typing_extensions import override

Html = NewType("Html", str)
"""A string representing rendered HTML."""


@runtime_checkable
class SupportsHtml(Protocol):
    """An interface shared by all HTML elements."""

    @override
    def __str__(self) -> Html: ...

    def _render(self) -> str: ...


EmptyChild = Literal[False, None]
"""An empty child type that may be passed to an element."""

ChildValue = Union[str, SupportsHtml, EmptyChild]
"""An acceptable value for a child element."""

Child = Union[ChildValue, Iterable[ChildValue]]
"""An acceptable type to be passed to an element."""
