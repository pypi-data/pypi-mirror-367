#!/usr/bin/env python3
"""
Tanat runner utils.
"""

import logging
import pathlib

from pypassist.utils.logging import temporary_console_logger
from tanat_cli_preset.utils import copy_preset

from .config import TanatRunnerConfig

LOGGER = logging.getLogger(__name__)


def init_config(dest, with_preset=True, exist_ok=False, logger_level="INFO"):
    """
    Initialize a new Tanat runner configuration

    Args:
        dest: Destination directory
        with_preset: If True, copy preset to destination
        exist_ok: If True, existing files will be overwritten
    """
    dest = pathlib.Path(dest).resolve()

    with temporary_console_logger(logging.getLogger(), logger_level):
        # pylint: disable=no-member
        TanatRunnerConfig.export(dest, exist_ok=exist_ok, makedirs=True)
        LOGGER.info("Tanat runner config exported to %s", dest)
        if with_preset:
            copy_preset(dest, exist_ok=exist_ok, makedirs=True)


ASCII_ART = """
╔═══════════════════════════════════════════════════════════════╗
║ ▗▄▄▄▖▗▄▖ ▗▖  ▗▖ ▗▄▖▗▄▄▄▖    ▗▄▄▖ ▗▖ ▗▖▗▖  ▗▖▗▖  ▗▖▗▄▄▄▖▗▄▄▖   ║
║   █ ▐▌ ▐▌▐▛▚▖▐▌▐▌ ▐▌ █      ▐▌ ▐▌▐▌ ▐▌▐▛▚▖▐▌▐▛▚▖▐▌▐▌   ▐▌ ▐▌  ║
║   █ ▐▛▀▜▌▐▌ ▝▜▌▐▛▀▜▌ █      ▐▛▀▚▖▐▌ ▐▌▐▌ ▝▜▌▐▌ ▝▜▌▐▛▀▀▘▐▛▀▚▖  ║
║   █ ▐▌ ▐▌▐▌  ▐▌▐▌ ▐▌ █      ▐▌ ▐▌▝▚▄▞▘▐▌  ▐▌▐▌  ▐▌▐▙▄▄▖▐▌ ▐▌  ║
╚═══════════════════════════════════════════════════════════════╝
"""
