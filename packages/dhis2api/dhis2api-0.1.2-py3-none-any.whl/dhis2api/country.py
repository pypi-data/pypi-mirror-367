import os
import requests
import logging
import pandas as pd
from datetime import datetime
from typing import List, Optional, Union
from .generate_params import GenerateParams

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Country:
    """
    A class for fetching and storing country-level data from an API.

    Attributes
    ----------
    base_url : str
        Base URL of the API endpoint.
    country : str
        Country code or identifier.
    dates : str
        Date range or date parameter for the data request.
    level : str, optional
        Geographic or administrative level for data extraction.
    folderpath : str, optional
        Directory path to save downloaded data.
    category : str, default "core"
        Data category to request.
    indicators : list, optional
        List of indicator codes to fetch.
    disaggregate : list, optional
        List of dimensions to disaggregate by.
    auth : tuple, optional
        Authentication credentials for the API (username, password).
    json_filepath : str, optional
        Path to JSON configuration file for parameters.

    Methods
    -------
    save_empty_file(idx: int):
        Saves an empty CSV file if no data is fetched or on initial request.
    request_and_save():
        Sends API requests for all parameters and saves responses to CSV.
    handle_successful_request(r, idx: int, today: str):
        Processes and saves data for successful API responses.
    handle_failed_request(r, idx: int, param):
        Logs and handles failed API requests.
    post_download_examine():
        Validates downloaded data against requested indicators.
    """
    def __init__(
        self,
        base_url: str,
        country: str,
        dates: str,
        level: str = None,
        folderpath: str = None,
        category="core",
        indicators: list = None,
        disaggregate: List = None,
        auth: tuple = None,
        json_filepath: str = None
    ):
        self.country = country
        self.generate_params = GenerateParams(
            country=country,
            dates=dates,
            level=level,
            category=[category],
            indicators=indicators,
            disaggregate=disaggregate,
            json_filepath=json_filepath
        )
        self.base_url = base_url
        self.auth = auth
        self.params = self.generate_params.get_params()
        self.disaggregate = disaggregate
        self.disaggregate_name = "".join(disaggregate) if disaggregate else ""
        self.folderpath = folderpath if folderpath else "./"
        self.filepath = None
        self.headers = None

    def save_empty_file(self, idx: int):
        """Saves an empty CSV file if required."""
        if not os.path.exists(self.filepath) or idx == 0:
            pd.DataFrame().to_csv(self.filepath, index=False)

    def request_and_save(self):
        """Requests data from the API and saves it to a CSV file."""
        today = datetime.today().strftime('%m-%d-%Y')
        self.filepath = f'{self.folderpath}{self.country}_{today}.csv'
        if self.disaggregate:
            self.filepath = f'{self.folderpath}{self.country}_{self.disaggregate_name}_{today}.csv'

        for idx, param in enumerate(self.params):
            try:
                r = requests.get(url=self.base_url, params=param,
                                 auth=self.auth, timeout=600)
                if r.status_code == 200:
                    self.handle_successful_request(r, idx, today)
                else:
                    self.handle_failed_request(r, idx, param)
            except requests.RequestException as e:
                logger.error("Request failed for %s: %s", self.country, e)
                self.save_empty_file(idx)

    def handle_successful_request(self, r, idx: int, today: str) -> None:
        """Handle a successful API request and save the data."""
        content = r.json()
        cols = [i["column"] for i in content["headers"]]
        temp = pd.DataFrame(content["rows"], columns=cols)
        if temp.empty:
            logger.warning("%d: No data fetched.", idx)
        else:
            temp["date_downloaded"] = today
            self.headers = cols
            mode = 'a' if os.path.exists(self.filepath) and idx > 0 else 'w'
            header = False if mode == 'a' else True
            temp.to_csv(self.filepath, mode=mode, header=header, index=False)
            logger.info("%d: Data downloaded successfully", idx)

    def handle_failed_request(self, r, idx: int, param) -> None:
        """Handles a failed API request."""
        logger.error("%d: Error %d fetching data for %s-%s", idx,
                     r.status_code, param['dimension'][1], param['dimension'][2])
        self.save_empty_file(idx)

    def post_download_examine(self):
        """Checks the differences between specified and downloaded indicators."""
        try:
            df = pd.read_csv(self.filepath)
            if len(df) == 0:
                logger.warning(
                    "Failed downloading data for %s.", self.filepath)
            else:
                download_set = set(df["dataid"].unique().tolist())
                original_indicators = [
                    i.strip() for i in self.generate_params.indicators.split(";")]
                original_set = set(original_indicators)
                difference = original_set - download_set
                if difference:
                    logger.warning(
                        "The following indicators were not downloaded: %s", difference)
                else:
                    logger.info(
                        "All indicators have been downloaded successfully.")
        except Exception as e:
            logger.error("Error examining downloaded file: %s", e)
