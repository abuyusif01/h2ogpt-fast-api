from pymongo import MongoClient
from dotenv import load_dotenv
import os


class Cursor:
    """init cursor object
    Members:
        user: str | None
        passwd: str | None
        host: str | None
        port: str | None
        db: str | None
        connection: MongoClient
        cursor: MongoClient
    """

    load_dotenv()

    user: str | None = os.getenv("MONGO_USER")
    passwd: str | None = os.getenv("MONGO_PASS")
    host: str | None = os.getenv("MONGO_HOST")
    port: str | None = os.getenv("MONGO_PORT")
    db: str | None = str(os.getenv("MONGO_DB"))
    try:
        connection = MongoClient(
            f"mongodb://{user}:{passwd}@{host}:{port}/?authMechanism=DEFAULT"
        )
        cursor = connection[db]
    except Exception as e:
        raise Exception(f"Failed to connect to db {repr(e)}")
