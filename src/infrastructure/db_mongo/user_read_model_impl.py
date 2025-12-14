"""User read model MongoDB implementation."""

from typing import List, Optional

from pymongo.collection import Collection
from pymongo.database import Database

from src.domain.users.value_objects import UserId
from src.infrastructure.db_mongo.client import get_mongo_database
from src.ports.users.user_read_model import UserReadModel


class MongoDBUserReadModel(UserReadModel):
    """MongoDB implementation of UserReadModel."""

    def __init__(self, database: Optional[Database] = None) -> None:
        """Initialize read model with MongoDB database.

        Args:
            database: MongoDB database instance (defaults to global database)
        """
        self._db = database or get_mongo_database()
        self._collection: Collection = self._db["users"]

    def get_by_id(self, user_id: UserId) -> Optional[dict]:
        """Get user read model by ID."""
        doc = self._collection.find_one({"id": str(user_id.value)})
        if doc:
            doc.pop("_id", None)  # Remove MongoDB _id
        return doc

    def search_by_email(self, email: str) -> List[dict]:
        """Search users by email."""
        cursor = self._collection.find(
            {"email": {"$regex": email, "$options": "i"}}
        ).limit(100)
        results = []
        for doc in cursor:
            doc.pop("_id", None)  # Remove MongoDB _id
            results.append(doc)
        return results

    def create(self, user_data: dict) -> None:
        """Create user read model."""
        self._collection.insert_one(user_data)

    def update(self, user_id: UserId, user_data: dict) -> None:
        """Update user read model."""
        self._collection.update_one(
            {"id": str(user_id.value)}, {"$set": user_data}, upsert=True
        )

    def delete(self, user_id: UserId) -> None:
        """Delete user read model."""
        self._collection.delete_one({"id": str(user_id.value)})


