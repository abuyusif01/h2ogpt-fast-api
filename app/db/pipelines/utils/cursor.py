from pymongo import MongoClient
from core.config import settings


class Cursor:
    """init cursor object
    Members:
        user: str | None
        passwd: str | None
        host: str | None
        port: str | None
        connection: MongoClient
    """

    user: str = settings.MONGO_USER
    passwd: str = settings.MONGO_PASS
    host: str = settings.MONGO_HOST
    port: int = settings.MONGO_PORT
    connection: MongoClient

    def __init__(self):
        try:
            self.connection = MongoClient(
                f"mongodb://{self.user}:{self.passwd}@{self.host}:{self.port}/?authMechanism=DEFAULT"
            )

        except Exception as e:
            raise Exception(f"Failed to connect to db {repr(e)}")
