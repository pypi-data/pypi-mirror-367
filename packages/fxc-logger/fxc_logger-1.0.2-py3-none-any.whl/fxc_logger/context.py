"""Context utilities for fxc-logger (ex Frexco PyLogger)."""

from __future__ import annotations

import asyncio
import uuid
from contextvars import ContextVar
from contextlib import contextmanager
from typing import Optional

_correlation_id_var: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    _correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id(auto_create: bool = True) -> Optional[str]:
    cid = _correlation_id_var.get()
    if cid is None and auto_create:
        cid = set_correlation_id()
    return cid


def clear_correlation_id() -> None:
    _correlation_id_var.set(None)


@contextmanager
def correlation_scope(correlation_id: Optional[str] = None):
    token = _correlation_id_var.set(correlation_id or str(uuid.uuid4()))
    try:
        yield
    finally:
        _correlation_id_var.reset(token)


def _extract_cid(*args, **kwargs) -> Optional[str]:
    if "correlation_id" in kwargs:
        return kwargs["correlation_id"]
    if args:
        first = args[0]
        return getattr(first, "correlation_id", None)
    return None


def with_new_correlation_id(func=None, *, extractor=_extract_cid):
    def decorator(f):
        if asyncio.iscoroutinefunction(f):

            async def async_wrapper(*args, **kwargs):  # type: ignore
                with correlation_scope(extractor(*args, **kwargs)):
                    return await f(*args, **kwargs)

            return async_wrapper

        def sync_wrapper(*args, **kwargs):  # type: ignore
            with correlation_scope(extractor(*args, **kwargs)):
                return f(*args, **kwargs)

        return sync_wrapper

    if func is not None:
        return decorator(func)
    return decorator
