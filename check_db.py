#!/usr/bin/env python3
from pymongo import MongoClient
import os

try:
    client = MongoClient(os.getenv('MONGO_HOST', 'mongodb'), 27017, serverSelectionTimeoutMS=5000)
    db = client.dbjungle
    count = db.movies.count_documents({})
    print(f"{count}")
except Exception as e:
    print("0")
