"""
RAG management module, supporting CRUD operations for multiple vector databases.
"""

from typing import Any, Dict, List, Optional
from .vector_stores.base import BaseVectorStore

class RAGManager:
    def __init__(self, vector_store: BaseVectorStore):
        self.vector_store = vector_store

    def create_col(self, name, vector_size=None, distance=None):
        """
        Create a new collection.
        Args:
            name (str): Name of the collection.
            vector_size (int, optional): Size of the vectors.
            distance (optional): Distance metric.
        """
        return self.vector_store.create_col(name, vector_size, distance)

    def insert(self, name, vectors: List, payloads: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        """
        Insert multiple vectors into a collection.
        Args:
            name (str): Name of the collection.
            vectors (List): List of vectors to insert.
            payloads (List[Dict], optional): List of payloads for each vector.
            ids (List[str], optional): List of IDs for each vector.
        """
        return self.vector_store.insert(name, vectors, payloads, ids)

    def insert_one(self, name, vector, payload=None, id=None):
        """
        Insert a single vector into a collection.
        Args:
            name (str): Name of the collection.
            vector: The vector to insert.
            payload (dict, optional): Payload for the vector.
            id (str, optional): ID for the vector.
        """
        return self.vector_store.insert_one(name, vector, payload, id)

    def delete(self, name, points: list) -> bool:
        """
        Delete vectors by a list of IDs.
        Args:
            name (str): Name of the collection.
            points (list): List of vector IDs to delete.
        Returns:
            bool: True if successful.
        """
        return self.vector_store.delete(name, points)

    def delete_one(self, name, vector_id: str) -> bool:
        """
        Delete a single vector by ID.
        Args:
            name (str): Name of the collection.
            vector_id (str): ID of the vector to delete.
        Returns:
            bool: True if successful.
        """
        return self.vector_store.delete_one(name, vector_id)

    def update(self, name, vector_id: str, vector, payload=None) -> bool:
        """
        Update a vector and its payload by ID.
        Args:
            name (str): Name of the collection.
            vector_id (str): ID of the vector to update.
            vector: The new vector.
            payload (dict, optional): The new payload.
        Returns:
            bool: True if successful.
        """
        return self.vector_store.update(name, vector_id, vector, payload)

    def get(self, name, vector_id: str):
        """
        Retrieve a vector by ID.
        Args:
            name (str): Name of the collection.
            vector_id (str): ID of the vector to retrieve.
        Returns:
            dict: The retrieved vector payload, or None if not found.
        """
        return self.vector_store.get(name, vector_id)

    def search(self, name, query_vector, top_k=5, filters=None, **kwargs):
        """
        Search for similar vectors in a collection.
        Args:
            name (str): Name of the collection.
            query_vector: The query vector.
            top_k (int, optional): Number of results to return.
            filters (dict, optional): Filter conditions.
            **kwargs: Additional arguments for vector store search.
        Returns:
            List[dict]: List of payloads for the matched vectors.
        """
        return self.vector_store.search(name, query_vector, top_k, filters, **kwargs)

    def list_cols(self):
        """
        List all collections.
        Returns:
            Any: Vector store collections response object.
        """
        return self.vector_store.list_cols()

    def delete_col(self, name):
        """
        Delete a collection by name.
        Args:
            name (str): Name of the collection to delete.
        Returns:
            Any: Vector store response object.
        """
        return self.vector_store.delete_col(name)

    def col_info(self, name):
        """
        Get information about a collection.
        Args:
            name (str): Name of the collection.
        Returns:
            Any: Vector store collection info response.
        """
        return self.vector_store.col_info(name)

    def list(self, name, filters=None, limit=100):
        """
        List all vectors in a collection with optional filters.
        Args:
            name (str): Name of the collection.
            filters (dict, optional): Filter conditions.
            limit (int, optional): Number of vectors to return.
        Returns:
            Any: Vector store scroll response.
        """
        return self.vector_store.list(name, filters, limit) 