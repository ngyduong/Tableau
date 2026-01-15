from __future__ import annotations

import argparse

from wrapper.config import ConfigWrapper
from wrapper.tableau_wrapper import TableauClient


def main(tc: TableauClient, cfg: ConfigWrapper, args: argparse.Namespace) -> None:

    print("Running hyper_api_create_extract")

    # Your logic here...
