#!/usr/bin/env python3
"""
Cluster class.
"""


class Cluster:
    """
    Class representing a cluster of objects (e.g., trajectories or sequences).
    """

    def __init__(self, cluster_id):
        """
        Initialize the cluster.

        Args:
            cluster_id: The ID of the cluster.
        """
        self.id = cluster_id
        self._items = []  # List of objects in the cluster (e.g., trajectory IDs)

    def add_item(self, item):
        """
        Add an object to the cluster.
        """
        self._items.append(item)

    def remove_item(self, item):
        """
        Remove an object from the cluster.
        """
        if item in self._items:
            self._items.remove(item)
        else:
            raise ValueError(f"Object {item} is not in the cluster.")

    def get_items(self):
        """
        Return the list of objects in the cluster.
        """
        return self._items

    @property
    def size(self):
        """
        Return the size of the cluster (number of elements).
        """
        return len(self._items)

    def __repr__(self):
        return f"Cluster(id={self.id}, size={self.size})"
