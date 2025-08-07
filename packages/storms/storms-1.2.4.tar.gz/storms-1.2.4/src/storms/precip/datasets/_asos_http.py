from calendar import month
import logging
from io import StringIO
import re
from typing import Any, Sequence
from urllib.parse import urlencode
from warnings import warn

import pandas as pd
import requests
from aiohttp_retry import RetryClient, RetryOptionsBase

from storms._datasource import _DataSource, async_retries
from storms._utils import datetime_like

logger = logging.getLogger(__name__)


class ASOS_http(_DataSource):
    def __init__(self, FAA: str):
        """Methods for pulling data from the Iowa  State University
        Environmental Mesonet:

        https://mesonet.agron.iastate.edu/ASOS/

        Parameters
        ----------
        FAA: str
            The FAA code of the station

        Returns
        -------

        """
        self.faa = self.FAA = FAA
        self.URL = "https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg2/access"
        self.latlon = None
        self.utc_offset = None
        self.get_meta()

    @staticmethod
    def map():
        """A folium map to help find asos stations. Using in
        jupyter notebook will display the map inline. Using in terminal
        will only produce a folium map object. The map can be saved to html
        with `map.save('path_to_html_file.html')`

        Returns
        -------
        folium.Map
            interactive map of active asos stations in Iowa mesonet's database

        Raises
        ------
        ModuleNotFoundError
            Error if folium not installed. Since this function is not imperative to the
            the library, folium is not included in major requirements.txt file

        Examples
        --------
        >>> from storms.precip import datasets as pds
        >>> pds.asos.map()
        >>> # if you are not in juptyer, you'll need to save to html
        >>> map.save('ASOS_Stations.html')
        """

        ...

    def get_meta(self):
        """ """
        with self.session_with_retries(timeout=15) as session:
            url = f"https://www.ncei.noaa.gov/access/homr/services/station/search?qid=FAA:{self.faa}"
            json = session.get(url).json()

        self._meta_json = json
        por = self._meta_json["stationCollection"]["stations"][0]["header"]["por"]
        self.por = dict(
            start=pd.Timestamp(por["beginDate"]),
            end=pd.Timestamp(por["endDate"].replace("Present", "now")),
        )
        if len(json["stationCollection"]["stations"]) > 1:
            raise UserWarning(
                "Found multiple stations in HORM meta data. ",
                "Please raise in issue in the package repository regarding this station. ",
                "Meta data cannot be found, lat and lon will not be set.",
            )
        try:
            station = json["stationCollection"]["stations"][0]
            self.latlon = (
                float(station["header"]["latitude_dec"]),
                float(station["header"]["longitude_dec"]),
            )
            self.utc_offset = int(
                station["location"]["geoInfo"]["utcOffsets"][0]["utcOffset"]
            )
        except Exception as e:
            print(
                "Failed collecting meta data for this station. Please raise an issue in the package repository.",
                str(e),
            )

    def request_dataframe(
        self,
        start: datetime_like,
        end: datetime_like,
        process_data: bool = True,
        parallel=False,
        progress: bool = True,
        timeout: int = 20,
        **kwargs,
    ) -> pd.DataFrame:
        """Request precipitation DataFrame with annual requests to Iowa Mesonet
        For potential faster data pulls for longer time periods, use with parallel=True

        https://mesonet.agron.iastate.edu/ASOS/

        Parameters
        ----------
        start: datetime_like
            Start date string that can be converted to Timestamp with pd.to_datetime

        end: datetime_like
            End date string that can be converted to Timestamp with pd.to_datetime

        process_data: bool
            Switch to process mesonet data dropping suspect values or not.
            Set to False to get all the raw data pulled from mesonet.
            Set to True to drop O precip values NP ptype values

        parallel: bool
            Switch to pull data asynchronously (can be much faster for longer data pulls), defaults to False

        progress: bool
            Switch to show tqdm bar for data download progress, defaults to True

        timeout: int
            Timeout in seconds for each request, defaults to 10.

        **kwargs: dict
            Keyword arguments to pass onto _async_request_dataframe or _sync_request_dataframe

        Returns
        -------
        pd.DataFrame
            DataFrame of precipitation records.

        Examples
        --------
        >>> from storms.precip import datasets as pds
        >>> bos = pds.asos("BOS")  #station ID for KBOS
        >>> # use parallel to download large datasets fast and process_data=True (default) to post process raw data, removing suspect values.
        >>> df = bos.request_dataframe("1/1/2010","1/1/2021", parallel=True)
        """
        return super().request_dataframe(
            start, end, process_data, parallel, progress, timeout, **kwargs
        )

    def _request_url(
        self,
        start: datetime_like,
        end: datetime_like,
        datatype: Sequence[str] = ["precip", "ptype"],
    ) -> str:
        """Get a formatted asos request URL for a given datatype. Default data type is precip
        for minutely precip and ptype for QAQC records of each value.

        See the request php code for more details
        https://github.com/akrherz/iem/blob/main/htdocs/request/asos

        Parameters
        ----------
        start: datetime_like
            Start date string that can be converted to Timestamp with pd.to_datetime

        end: datetime_like
            End date string that can be converted to Timestamp with pd.to_datetime

        datatype: Sequence[str]
            List of data types to request from the mesonet, defaults to ["precip", "

        Returns
        -------
        str
            Iowa Mesonet URL for requested asus data

        """
        st = pd.to_datetime(start)  # .tz_localize(self.TZ)
        # ed = pd.to_datetime(end)  # .tz_localize(self.TZ)

        if self.utc_offset is not None:
            st -= pd.Timedelta(f"{self.utc_offset}h")
            # ed -= pd.Timedelta(f"{self.utc_offset}h")

        return f"{self.URL}/{st.year}/{st.month:02d}/asos-1min-pg2-K{self.faa.upper()}-{st.year}{st.month:02d}.dat"

    def _sync_request_dataframe(
        self,
        start: datetime_like,
        end: datetime_like,
        process_data: bool = True,
        pull_freq: str = "MS",
        timeout: int = 20,
    ) -> pd.DataFrame:
        """Request precipitation DataFrame with synchronous annual requests to Iowa Mesonet
        For potential faster data pulls for longer time periods, use the
        asynchronous request method `_async_request_dataframe`.

        Parameters
        ----------
        start: datetime_like
            Start date string that can be converted to Timestamp with pd.to_datetime

        end: datetime_like
            End date string that can be converted to Timestamp with pd.to_datetime

        process_data: bool
            Switch to process mesonet data dropping suspect values or not.
            Set to False to get all the raw data pulled from mesonet.
            Set to True to drop O precip values NP ptype values

        pull_freq: str
            Pandas offset string for the length of time for each async data request, defaults to annual (AS).

        Returns
        -------
        pd.DataFrame
            DataFrame of precipitation records.

        """
        data = self._sync_request_data_series(start, end, pull_freq, timeout)

        datastr = "\n".join(data)

        records = []
        def process_record(record: list[str]) -> list[Any]:
            out = []
            site = record[1][:3]
            year = record[1][3:7]
            month = record[1][7:9]
            day = record[1][9:11]
            utc_hour = record[1][15:17]
            utc_minute = record[1][17:19]
            
            ptype = record[2]
            precip = record[4]
        for line in datastr.split("\n"):
            records = line.split()
            if len(records) != 11:
                logger.warning(
                    f"Malformed record in data: {line}. Expected 11 fields, got {len(records)}."
                )
                continue
            else:


        with StringIO(datastr) as s:
            df = pd.read_csv(
                s,
                header=None,
                sep="\s+",
                names=["ID", "DTCode", "ptype", "precip", "ptype"],
                usecols=range(5),
            )

        if process_data:
            self._update_progress_description("Processing")
            df = self._process_data(df)

        self._close_progress()

        return df

    def _sync_request_data(
        self, start: datetime_like, end: datetime_like, session: requests.Session
    ) -> str:
        """Synchronously Request minutely rainfall CSV data from mesonet

        Parameters
        ----------
        start: datetime_like
            Start date string that can be converted to Timestamp with pd.to_datetime

        end: datetime_like
            End date string that can be converted to Timestamp with pd.to_datetime

        session: requests.Session
            requests Session to use for API calls

        Returns
        -------
        str
            string of csv data returned from mesonet

        """
        url = self._request_url(start, end, ["precip", "ptype"])
        with session.get(url) as response:
            return response.text

    async def _async_request_dataframe(
        self,
        start: datetime_like,
        end: datetime_like,
        process_data: bool = True,
        pull_freq: str = "YS",
        conn_limit: int = 5,
        retry_options: RetryOptionsBase = async_retries,
        timeout: int = 20,
    ) -> pd.DataFrame:
        """
        Request precipitation DataFrame with asynchronous annual requests to Iowa Mesonet

        This is an async function and must be awaited as::

            df = await gage._async_request_dataframe(start = '1/1/2020', end = '1/1/2021')

        Parameters
        ----------
        start: datetime_like
            Start date string that can be converted to Timestamp with pd.to_datetime

        end: datetime_like
            End date string that can be converted to Timestamp with pd.to_datetime

        process_data: bool
            Switch to process mesonet data dropping suspect values or not.
            Set to False to get all the raw data pulled from mesonet.
            Set to True to drop O precip values NP ptype values

        pull_freq: str
            Pandas offset string for the length of time for each async data request, defaults to annual (AS).

        conn_limit: int
            Connection limit for aiohttp session, defaults to 5

        retry_options: RetryOptionsBase
            Retry options to pass to aiohttp_retry client

        timeout: int
            Timeout in seconds for each request, defaults to 10.

        Returns
        -------
        pd.DataFrame
            DataFrame of precipitation records.

        """

        # I think the mesonet limits to 5 connections over 300s or 300ms?
        # setting conn_limit to 5 for now, seems to work okay
        # https://github.com/akrherz/iem/blob/main/include/throttle.php
        data = await self._async_request_data_series(
            start, end, pull_freq, conn_limit, retry_options, timeout
        )
        datastr = "\n".join(data)
        with StringIO(datastr) as s:
            df = pd.read_csv(
                s,
                header=None,
                names=["FAA", "Station", "dtUTC", "precip", "ptype"],
                usecols=range(5),
            )
        if process_data:
            self._update_progress_description("Processing")
            df = self._process_data(df)

        self._close_progress()

        return df

    async def _async_request_data(
        self, start: datetime_like, end: datetime_like, session: RetryClient
    ) -> str:
        """
        Request minutely rainfall CSV data from Iowa mesonet

        Parameters
        ----------
        start: datetime_like
            Start date string that can be converted to Timestamp with pd.to_datetime

        end: datetime_like
            End date string that can be converted to Timestamp with pd.to_datetime

        session: aiohttp_retry.RetryClient
            aiohttp_retry RetryClient to use for API calls

        Returns
        -------
        str
            Returns csv string from API request.
        """

        url = self._request_url(start, end, ["precip", "ptype"])
        # async json response
        # https://docs.aiohttp.org/en/stable/client_quickstart.html#json-response-content
        async with session.get(url) as response:
            text = await response.text()
            return "\n".join(text.split("\n")[1:])

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process raw asos data response into a cleaner dataframe.
        Routine drops NP data pulled from API, tried to convert UTC
        datetimes into local time based on info from HOMR, then reorders columns.

        Asos Data Flags
        -------------
        UP: Unknown Precipitation
        -R, R, +R: Liquid Rain (light, moderate, heavy)
        -FZR, FZR: Freezeing Rain (light, moderate)
        S-, S, S+: Frozen Rain (snow) (light moderate, heavy)
        NP: No precipitation

        Parameters
        ----------
        df: pd.DataFrame
            DataFrame returned from _async_request_dataframe or _sync_request_dataframe

        Returns
        -------
        pd.DataFrame
            pandas DataFrame of cleaned data

        """

        df["dtUTC"] = pd.to_datetime(df["dtUTC"])

        # sometimes missing flags show up in value column
        missing_idx = df.loc[df.precip == "M"].index
        df.loc[missing_idx, "precip"] = 0
        df.loc[missing_idx, "ptype"] = "M"
        df["precip"] = df["precip"].astype(float)
        num_missing = int((df.ptype == "M").sum())
        if num_missing > 0:
            logger.warning(
                f"{num_missing} missing values ({num_missing/len(df)*100:.2f}%) from gauge {self.faa}"
            )

        # drop zeros and NP values
        no_precip = (df.ptype == "NP") & (df.precip > 0)
        precip = (df.ptype != "NP") & (df.precip > 0)
        logger.debug(f"Dropping {df.loc[no_precip,'precip'].sum()} inches of NP values")
        df = df.drop(df.loc[~precip].index)

        if self.utc_offset is None:
            warn(
                "No timezone info set (self.utc_offset), cannot convert datetime to LST"
            )
            return df.reindex(["dtUTC", "precip", "ptype"], axis=1)

        else:
            df["dtLocal"] = df["dtUTC"] + pd.Timedelta(f"{self.utc_offset}h")
            return df.reindex(["dtLocal", "dtUTC", "precip", "ptype"], axis=1)
