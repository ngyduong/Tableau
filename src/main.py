"""
Main
====================================
The core module of the project
"""

from __future__ import annotations

import argparse
import sys
from typing import Callable, Dict

from src.scripts.hyper_api_create_extract import main as run_hyper_api_create_extract
from wrapper.config import ConfigWrapper
from wrapper.tableau_wrapper import TableauClient

ScriptFn = Callable[[TableauClient, ConfigWrapper, argparse.Namespace], None]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Project entrypoint")
    parser.add_argument(
        "--script",
        required=True,
        choices=[
            "hyper_api_create_extract",
            "hyper_api_create_hyper",
            "hyper_api_publish_hyper",
        ],
        help="Which script to run",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # Load & validate config once (raises ValueError if missing env vars)
    cfg = ConfigWrapper()

    scripts: Dict[str, ScriptFn] = {
        "hyper_api_create_extract": run_hyper_api_create_extract,
    }

    script_fn = scripts.get(args.script)
    if not script_fn:
        print(f"No script found: {args.script}", file=sys.stderr)
        return 2

    # One shared Tableau session for the whole run
    with TableauClient() as tc:
        script_fn(tc, cfg, args)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
