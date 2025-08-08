#!/usr/bin/env python3
"""
MOOC-events zenodo accessor.
"""

import pandas as pd

from ..zenodo import ZenodoAccessor


class MOOCEventsZenodoAccessor(ZenodoAccessor, register_name="mooc_events"):
    """
    MOOCEvents zenodo accessor.
    """

    def __init__(self, cache_dir=None):
        ZenodoAccessor.__init__(
            self,
            record_id=16421055,
            filename="mooc_events.csv",
            cache_dir=cache_dir,
        )

    def _access_impl(self):
        """
        MOOCEvent access implementation.

        Returns:
            mooc_event dataframe
        """
        return pd.read_csv(self.local_path, parse_dates=["timecreated"])
