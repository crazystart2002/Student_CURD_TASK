from fastapi import FastAPI
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from routes import router


app=Fla

app.include_router(router)


if __name__=="main":
    app.run()