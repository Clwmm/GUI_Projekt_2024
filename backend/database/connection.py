from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pydantic import BaseModel
from backend.models.transaction import Coin

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

MONGO_URI = os.environ.get("MONGODB")
DB_NAME = os.environ.get("DB_NAME")

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        # self.client.drop_database(db_name)
        self.db = self.client[db_name]
        self.collection = self.db["guiDB"]

    def get_users_collection(self) -> Collection:
        return self.db["users"]

    def get_user_to_transaction_collection(self) -> Collection:
        return self.db["user_to_transaction"]

    def get_transactions_collection(self) -> Collection:
        return self.db["transaction"]

    def get_coins_collection(self) -> Collection:
        return self.db["coins"]

    def get_coin_to_user_collection(self) -> Collection:
        return self.db["coin_to_user"]


mongo_instance = MongoDB(MONGO_URI, DB_NAME)

coins_collection = mongo_instance.get_coins_collection()
new_coin_1 = Coin(name="usd")
new_coin_2 = Coin(name="eth")
new_coin_3 = Coin(name="btc")
new_coin_4 = Coin(name="sol")
coins_collection.insert_one(new_coin_1.dict())
coins_collection.insert_one(new_coin_2.dict())
coins_collection.insert_one(new_coin_3.dict())
coins_collection.insert_one(new_coin_4.dict())


try:
    print("Connecting to DB...")
    mongo_instance.client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Connetction Error: ", e)
