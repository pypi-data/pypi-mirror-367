#!/usr/bin/env python
"""TanaT CLI."""

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from .runner.utils import init_config

LOGGER = logging.getLogger(__name__)


def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        description="TanaT command line interface",
        epilog="Examples:\n"
        "  Execute a TanaT runner:  python -m tanat run --config-path <path/to/> "
        "--config-name <config_name>\n"
        "  Init config:     python -m tanat init --path <path> --with-preset --exist-ok",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    # Run command
    subparsers.add_parser(
        "run",
        help="Execute a TanaT runner",
        description="Execute a TanaT runner with the specified configuration",
    )

    # Init command
    init = subparsers.add_parser(
        "init",
        help="Initialize a new configuration",
        description="Create a new configuration directory with default templates",
    )
    init.add_argument("path", help="Path for the new configuration", type=Path)
    init.add_argument(
        "--exist-ok",
        dest="exist_ok",
        help="Overwrite existing configuration",
        action="store_true",
    )
    init.add_argument(
        "--with-preset",
        dest="with_preset",
        help="Copy preset to destination",
        action="store_true",
    )

    return parser


def script_main():
    """TanaT main function"""
    parser = create_parser()
    args, remaining = parser.parse_known_args()

    if args.command == "run":
        cmd = [sys.executable, "-m", "tanat.runner.app.hydra"] + remaining
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as err:
            sys.exit(err.returncode)
        except KeyboardInterrupt:
            pass
    elif args.command == "init":
        sys.exit(init_config(args.path, args.with_preset, args.exist_ok))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    script_main()
