from fastapi import Depends, FastAPI
from pydantic import RedisDsn

from farl import AsyncFarl, FarlMiddleware, rate_limit


# Using Redis backend
redis_uri = RedisDsn("redis://")  # or "redis://"
farl = AsyncFarl(redis_uri=redis_uri)

app = FastAPI()
app.add_middleware(
    FarlMiddleware,
    farl=farl,
)


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
