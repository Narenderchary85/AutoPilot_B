from pymongo import MongoClient
from src.utils.config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.autopilot

users_collection = db.users
google_tokens_collection = db.google_tokens
