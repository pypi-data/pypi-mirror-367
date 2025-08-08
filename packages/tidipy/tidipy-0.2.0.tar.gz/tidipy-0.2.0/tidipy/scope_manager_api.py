from typing import Optional

from .resolver import Resolver
from .scope_context import ScopeContext
from .scope_manager import scope_manager
from .scope_type import parse_scope_type


def ensure_scope(
    scope_id: str = 'root',
    scope_type: str = 'root',
    parent_id: Optional[str] = None,
    context: Optional[dict[str, str]] = None
) -> None:
    if parent_id is None and scope_id != 'root':
        parent_id = 'root'
    return scope_manager.ensure_scope(
        scope_id=scope_id,
        scope_type=parse_scope_type(scope_type),
        parent_id=parent_id,
        context=ScopeContext(context) if context is not None else None
    )


def get_resolver(scope_id: str = 'root') -> Resolver:
    return scope_manager.get_resolver(scope_id)


def clear_scope(scope_id: str) -> None:
    scope_manager.clear_scope(scope_id=scope_id)


def reset() -> None:
    scope_manager.reset()
