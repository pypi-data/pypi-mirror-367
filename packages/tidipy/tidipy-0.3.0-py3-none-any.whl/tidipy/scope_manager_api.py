from typing import Optional

from .resolver import Resolver
from .scope_context import ScopeContext
from .scope_manager import scope_manager
from .scope_type import parse_scope_type, RootType


def ensure_scope(
    scope_id: str,
    scope_type: str,
    parent_id: str = 'root',
    context: Optional[dict[str, str]] = None
) -> None:
    scope_manager.ensure_scope(
        scope_id=scope_id,
        scope_type=parse_scope_type(scope_type),
        parent_id=parent_id,
        context=ScopeContext(context) if context is not None else None
    )


def ensure_root_scope(
    context: Optional[dict[str, str]] = None
) -> None:
    scope_manager.ensure_scope(
        scope_id='root',
        scope_type=RootType(),
        parent_id=None,
        context=ScopeContext(context) if context is not None else None
    )


def get_resolver(scope_id: str = 'root') -> Resolver:
    return scope_manager.get_resolver(scope_id)


def clear_scope(scope_id: str) -> None:
    scope_manager.clear_scope(scope_id=scope_id)


def reset() -> None:
    scope_manager.reset()
