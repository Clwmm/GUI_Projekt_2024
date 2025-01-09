from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pydantic import BaseModel

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

MONGO_URI = os.environ.get("MONGODB")
DB_NAME = os.environ.get("DB_NAME")

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db["guiDB"]

    def get_collections(self, collection_name: str) -> Collection:
        return self.db[collection_name]

mongo_instance = MongoDB(MONGO_URI, DB_NAME)

try:
    print("Connecting to DB...")
    mongo_instance.client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connetction Error: ", e)
