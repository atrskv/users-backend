import dotenv

dotenv.load_dotenv()

import uvicorn
from fastapi import FastAPI

from app.db.engine import init_db
from app.routers import status, users

app = FastAPI()

app.include_router(status.router)
app.include_router(users.router)


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="localhost", port=8002)
