from collections.abc import Awaitable, Callable, Sequence
from typing import Protocol, TypeVar

import limits
import limits.aio
from limits import RateLimitItem
from pydantic import networks

from farl.utils import RateLimitDictValue, RateLimitTimeArg


Key = str
KeyResult = Key | Sequence[Key]
GetKeyDependency = Callable[..., KeyResult | Awaitable[KeyResult]]


CostResult = int
GetCostDependency = Callable[..., CostResult | Awaitable[CostResult]]


RateLimitArgument = (
    str
    | RateLimitItem
    | Sequence[RateLimitItem]
    | RateLimitTimeArg
    | Sequence[RateLimitTimeArg]
    | RateLimitDictValue
    | Sequence[RateLimitDictValue]
)
GetRateLimitArgumentDependency = Callable[
    ...,
    RateLimitArgument | Awaitable[RateLimitArgument],
]


class RedisDsn(networks.RedisDsn):
    _constraints = networks.UrlConstraints(
        allowed_schemes=[
            "redis",
            "rediss",
            "redis+sentinel",
            "redis+cluster",
        ],
        default_host="localhost",
        default_port=6379,
        default_path="/0",
        host_required=True,
    )


_T = TypeVar("_T")


class _FarlProtocol(Protocol[_T]):
    limiter: _T
    namespace: str | None


FarlProtocol = _FarlProtocol[limits.strategies.RateLimiter]
AsyncFarlProtocol = _FarlProtocol[limits.aio.strategies.RateLimiter]
AnyFarlProtocol = FarlProtocol | AsyncFarlProtocol
