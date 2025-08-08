#!/usr/bin/env python3
"""
Mvad zenodo accessor.
"""

import pandas as pd

from ..zenodo import ZenodoAccessor


class MvadZenodoAccessor(ZenodoAccessor, register_name="mvad"):
    """
    Mvad zenodo accessor.
    """

    def __init__(self, cache_dir=None):
        ZenodoAccessor.__init__(
            self,
            record_id=16367106,
            filename="data_mvad.csv",
            cache_dir=cache_dir,
        )

    def _access_impl(self):
        """
        Mvad access implementation.

        Returns:
            mvad dataframe
        """
        return pd.read_csv(self.local_path, parse_dates=["start", "end"])
