import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

# Required fields that every animal record must include before being inserted
REQUIRED_FIELDS = ["Animal Type", "Breed", "Name"]


class AnimalShelter(object):
    """CRUD operations for Animal collection in MongoDB"""

    def __init__(self, host='localhost', port=27017, db='AAC', collection='animals'):
        # Enhancement 1: Load credentials from environment variables instead of hardcoding them
        # For local MongoDB with no auth, MONGO_USER and MONGO_PASS can be empty or unset
        username = os.environ.get("MONGO_USER", "")
        password = os.environ.get("MONGO_PASS", "")

        try:
            # Connect without credentials if both are empty (local dev), otherwise use them
            if username and password:
                self.client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}')
            else:
                self.client = MongoClient(host, port)
            self.database = self.client[db.strip()]
            self.collection = self.database[collection]
            print("Connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    def create(self, data):
        if data and isinstance(data, dict):
            # Enhancement 2: Check that required fields exist before allowing the insert
            # Prevents incomplete animal records from being saved to the database
            missing = [field for field in REQUIRED_FIELDS if field not in data]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")

            try:
                result = self.collection.insert_one(data)
                return True if result.inserted_id else False
            except Exception as e:
                print(f"Create error: {e}")
                return False
        else:
            raise ValueError("Invalid data. Please provide a non-empty dictionary.")

    def read(self, query):
        # Return all documents matching the query, or empty list on error
        try:
            results = self.collection.find(query)
            return list(results)
        except Exception as e:
            print(f"Read error: {e}")
            return []

    def update(self, query, new_values):
        # Enhancement 3: Block empty queries to prevent accidentally updating every document
        if not query:
            raise ValueError("Query cannot be empty. Provide a filter to target specific documents.")

        try:
            result = self.collection.update_many(query, {"$set": new_values})
            return result.modified_count
        except PyMongoError as e:
            print(f"Update error: {e}")
            return 0

    def delete(self, query):
        # Enhancement 3: Block empty queries to prevent accidentally wiping the entire collection
        if not query:
            raise ValueError("Query cannot be empty. Provide a filter to target specific documents.")

        try:
            result = self.collection.delete_many(query)
            return result.deleted_count
        except PyMongoError as e:
            print(f"Delete error: {e}")
            return 0
