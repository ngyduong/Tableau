from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
from tableauhyperapi import (
    Connection,
    CreateMode,
    HyperProcess,
    Telemetry,
    escape_string_literal,
)

from src.utils.log_duration import log_duration
from src.wrapper.config import ConfigWrapper
from src.wrapper.tableau_wrapper import TableauClient

logger = logging.getLogger(__name__)


def main(tsc: TableauClient, cfg: ConfigWrapper, args: argparse.Namespace) -> None:
    logger.info("Starting script: generate_hyper")

    with log_duration("generate_hyper"):

        tmp_parquet = Path("temp/generate_hyper/pokemon.parquet")
        tmp_parquet.parent.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv("sample_data/pokemon.csv", sep=",", encoding="utf-8", header=0)
        df.to_parquet(tmp_parquet, index=False)

        schema_name = "Extract"
        table_name = "Extract"

        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(
                endpoint=hyper.endpoint,
                database="temp/generate_hyper/pokemon.hyper",
                create_mode=CreateMode.CREATE_AND_REPLACE,
            ) as connection:

                connection.catalog.create_schema(schema_name)
                schema_table = f'"{schema_name}"."{table_name}"'

                query = (
                    f"CREATE TABLE {schema_table} AS "
                    f"(SELECT * FROM external({escape_string_literal(str(tmp_parquet.resolve()))}, FORMAT => 'parquet'))"
                )
                connection.execute_command(query)

    logger.info("Script finished: generate_hyper")
