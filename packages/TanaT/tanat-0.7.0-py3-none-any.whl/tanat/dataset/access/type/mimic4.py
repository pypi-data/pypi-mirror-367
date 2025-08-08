#!/usr/bin/env python3
"""
Mimic4 zenodo accessor.
"""

import sqlite3

from ..zenodo import ZenodoAccessor


class Mimic4ZenodoAccessor(ZenodoAccessor, register_name="mimic4"):
    """
    Mimic4 zenodo accessor.
    """

    def __init__(self, cache_dir=None):
        ZenodoAccessor.__init__(
            self,
            record_id=16368465,
            filename="mimic4.db",
            cache_dir=cache_dir,
        )

    def _access_impl(self):
        """
        Mimic4 access implementation.

        Returns:
            mvad dataframe
        """
        return sqlite3.connect(self.local_path)
