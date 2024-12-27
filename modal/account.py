from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]




