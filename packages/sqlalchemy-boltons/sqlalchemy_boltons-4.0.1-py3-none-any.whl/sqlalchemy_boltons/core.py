from __future__ import annotations

import sqlalchemy as sa


__all__ = ["count1", "bytes_startswith", "bytes_prefix_upper_bound"]

_SQLExpression = object


def bytes_prefix_upper_bound(prefix: bytes) -> bytes | None:
    stripped = prefix.rstrip(b"\xff")
    if not stripped:
        return None
    return b"".join((memoryview(stripped)[:-1], bytes((stripped[-1] + 1,))))


def bytes_startswith(operand: _SQLExpression, prefix: bytes) -> _SQLExpression:
    """
    Produces SQL equivalent to ``operand.startswith(prefix)``, but which works correctly for BLOB-like columns.

    As an example, the resulting SQL for ``bytes_startswith(x, b"abc")`` is something like
    ``(x >= b"abc") & (x < b"abd")``.
    """
    expr = operand >= prefix
    if upper := bytes_prefix_upper_bound(prefix):
        expr = expr & (operand < upper)
    return expr


def count(select_from=None, count_argument=None):
    """
    Produces ``COUNT(*)`` if *select_from* is None, otherwise ``SELECT COUNT(*) FROM select_from``. This is a shorthand
    for ``sa.select(sa.func.count()).select_from(select_from)``.
    """
    expr = sa.func.count() if count_argument is None else sa.func.count(count_argument)
    return expr if select_from is None else sa.select(expr).select_from(select_from)


def count1(select_from=None):
    """
    Produces ``COUNT(1)``.
    """
    return count(select_from, sa.text("1"))
