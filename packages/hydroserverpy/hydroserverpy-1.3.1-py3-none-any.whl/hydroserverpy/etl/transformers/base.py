from abc import ABC, abstractmethod
import logging
from typing import Union
from hydroserverpy.etl.timestamp_parser import TimestampParser
import pandas as pd


class Transformer(ABC):
    def __init__(self, settings: object):
        self.timestamp = settings["timestamp"]
        self.timestamp_key: Union[str, int] = self.timestamp["key"]

        if isinstance(self.timestamp_key, int):
            # Users will always interact in 1-based, so if the key is a column index, convert to 0-based
            self.timestamp_key = self.timestamp_key - 1

        self.timestamp_parser = TimestampParser(self.timestamp)

    @abstractmethod
    def transform(self, *args, **kwargs) -> None:
        pass

    @property
    def needs_datastreams(self) -> bool:
        return False

    def standardize_dataframe(self, df: pd.DataFrame, payload_mappings):
        rename_map = {
            mapping["sourceIdentifier"]: mapping["targetIdentifier"]
            for mapping in payload_mappings
        }

        df.rename(
            columns={self.timestamp_key: "timestamp", **rename_map},
            inplace=True,
        )

        # Verify timestamp column is present in the DataFrame
        if "timestamp" not in df.columns:
            message = f"Timestamp column '{self.timestamp_key}' not found in data."
            logging.error(message)
            raise ValueError(message)

        # verify datastream columns
        expected = set(rename_map.values())
        missing = expected - set(df.columns)
        if missing:
            raise ValueError(
                "The following datastream IDs are specified in the config file but their related keys could not be "
                f"found in the source system's extracted data: {missing}"
            )

        # keep only timestamp + datastream columns; remove the rest inplace
        to_keep = ["timestamp", *expected]
        df.drop(columns=df.columns.difference(to_keep), inplace=True)

        df["timestamp"] = self.timestamp_parser.parse_series(df["timestamp"])

        df.drop_duplicates(subset=["timestamp"], keep="last")
        logging.info(f"standardized dataframe created: {df.shape}")
        logging.info(f"{df.info()}")
        logging.info(f"{df.head()}")

        return df
