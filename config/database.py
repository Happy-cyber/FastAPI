import environ
from pymongo import MongoClient

# ----------------------------------------------------------------------------------------------------------------------
# Initial environment instance
env = environ.Env()
environ.Env.read_env()


class Database:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def get_collection(self, collection_name: str):
        return self.db[collection_name]


# Create an instance of Database class
db = Database(env("DB_URI"), env("DB_NAME"))
