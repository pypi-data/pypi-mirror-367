#!/usr/bin/env python3
"""
TanaT hydra App Runner
"""

from pypassist.optional.runner.hydra import hydra_main
from pypassist.utils.hydra import get_config_path

from .core import core_tanat_app


@hydra_main(version_base=None, config_path=str(get_config_path()), config_name="config")
def tanat_app(cfg):
    """TanaT application main function."""
    return core_tanat_app(cfg)


if __name__ == "__main__":
    tanat_app()  # pylint: disable=E1120
