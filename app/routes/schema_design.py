from fastapi import APIRouter
from pymongo import MongoClient
import os

router = APIRouter()

client = MongoClient(os.getenv("MONGO_URL"))
db = client["travelloDB"]


def get_schema(collection):
    sample = collection.find().limit(50)
    schema = {}

    for doc in sample:
        for key, value in doc.items():
            dtype = type(value).__name__

            if key in schema:
                if dtype not in schema[key]:
                    schema[key].append(dtype)
            else:
                schema[key] = [dtype]

    return schema


@router.get("/db-schema")
def db_schema():
    result = {}
    collections = db.list_collection_names()

    for name in collections:
        result[name] = get_schema(db[name])

    return result