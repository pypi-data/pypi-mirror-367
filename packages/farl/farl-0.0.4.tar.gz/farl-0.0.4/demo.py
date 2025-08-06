from fastapi import Depends, FastAPI
from pydantic import RedisDsn

from farl import (
    AsyncFarl,
    FarlError,
    farl_exceptions_handler,
    rate_limit,
)


# Using Redis backend
redis_uri = RedisDsn("redis://")  # or "redis://"
farl = AsyncFarl(redis_uri=redis_uri)

app = FastAPI()
app.add_exception_handler(FarlError, farl_exceptions_handler)


@app.get(
    "/",
    dependencies=[
        Depends(
            rate_limit({"amount": 1}),
        )
    ],
)
async def pre_minute_1_request():
    return {"message": "ok"}
