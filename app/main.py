from contextlib import asynccontextmanager

import dotenv

dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI

from app.db.engine import init_db
from app.routers import status, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(status.router)
app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8002)
