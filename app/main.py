import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.routers import status, users

app: FastAPI = FastAPI()

app.include_router(status.router)
app.include_router(users.router)

_ = add_pagination(app)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8002)
