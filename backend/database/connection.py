from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from pydantic import BaseModel
from backend.models.transaction import Coin, Admin

from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

MONGO_URI = os.environ.get("MONGODB")
DB_NAME = os.environ.get("DB_NAME")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

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

    def get_admin_collection(self) -> Collection:
        return self.db["admin"]


print("Starting MongoDB instance...")
mongo_instance = MongoDB(MONGO_URI, DB_NAME)
print("\tSuccessfully created MongoDB instance!")

try:
    print("Connecting to DB...")
    mongo_instance.client.admin.command('ping')
    print("\tSuccessfully connected to DB!")
except Exception as e:
    print("Connetction Error: ", e)

coins_collection = mongo_instance.get_coins_collection()
new_coin_1 = Coin(name="usd")
new_coin_2 = Coin(name="eth")
new_coin_3 = Coin(name="btc")
if not coins_collection.find_one({"name": new_coin_1.name}):
    coins_collection.insert_one(new_coin_1.dict())
if not coins_collection.find_one({"name": new_coin_2.name}):
    coins_collection.insert_one(new_coin_2.dict())
if not coins_collection.find_one({"name": new_coin_3.name}):
    coins_collection.insert_one(new_coin_3.dict())

admin_collection = mongo_instance.get_admin_collection()
new_admin = Admin(email=ADMIN_EMAIL)
if not admin_collection.find_one({"email": new_admin.email}):
    admin_collection.insert_one(new_admin.dict())
