"""MongoDB client configuration."""

from pymongo import MongoClient
from pymongo.database import Database

from src.config.settings import settings

# Create MongoDB client
mongo_client: MongoClient = MongoClient(
    settings.MONGODB_URL,
    serverSelectionTimeoutMS=5000,
)


def get_mongo_database() -> Database:
    """Get MongoDB database instance.

    Returns:
        MongoDB database
    """
    return mongo_client[settings.MONGODB_DB]


