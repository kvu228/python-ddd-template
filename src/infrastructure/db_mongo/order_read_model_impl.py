"""Order read model MongoDB implementation."""

from typing import List, Optional

from pymongo.collection import Collection
from pymongo.database import Database

from src.domain.orders.value_objects import OrderId
from src.domain.users.value_objects import UserId
from src.infrastructure.db_mongo.client import get_mongo_database
from src.ports.orders.order_read_model import OrderReadModel


class MongoDBOrderReadModel(OrderReadModel):
    """MongoDB implementation of OrderReadModel."""

    def __init__(self, database: Optional[Database] = None) -> None:
        """Initialize read model with MongoDB database.

        Args:
            database: MongoDB database instance (defaults to global database)
        """
        self._db = database or get_mongo_database()
        self._collection: Collection = self._db["orders"]

    def get_by_id(self, order_id: OrderId) -> Optional[dict]:
        """Get order read model by ID."""
        doc = self._collection.find_one({"id": str(order_id.value)})
        if doc:
            doc.pop("_id", None)  # Remove MongoDB _id
        return doc

    def get_by_user_id(self, user_id: UserId) -> List[dict]:
        """Get orders by user ID."""
        cursor = self._collection.find({"user_id": str(user_id.value)}).sort(
            "created_at", -1
        )
        results = []
        for doc in cursor:
            doc.pop("_id", None)  # Remove MongoDB _id
            results.append(doc)
        return results

    def create(self, order_data: dict) -> None:
        """Create order read model."""
        self._collection.insert_one(order_data)

    def update(self, order_id: OrderId, order_data: dict) -> None:
        """Update order read model."""
        self._collection.update_one(
            {"id": str(order_id.value)}, {"$set": order_data}, upsert=True
        )

    def delete(self, order_id: OrderId) -> None:
        """Delete order read model."""
        self._collection.delete_one({"id": str(order_id.value)})


