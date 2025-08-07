import asyncio
import logging
import sys
from asyncio import TimeoutError
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any, List, Sequence, Union

import pandas as pd
from aiohttp import (
    ClientSession,
    ClientTimeout,
    TCPConnector,
    TraceRequestStartParams,
)
from aiohttp_retry import ExponentialRetry, RetryClient, RetryOptionsBase
from numpy import ndarray
from requests import Session
from requests.adapters import HTTPAdapter
from tqdm.autonotebook import tqdm
from urllib3.util.retry import Retry

from storms._utils import async_runner, datetime_like

handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(handlers=[handler])
logger = logging.getLogger(__name__)

sync_retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[502, 503, 504])
async_retries = ExponentialRetry(
    attempts=5, start_timeout=0.1, exceptions={TimeoutError}
)


class SessionWithTimeout(Session):
    def __init__(self, timeout=10):
        super().__init__()
        self._timeout = timeout

    def request(self, *args, **kwargs):
        if "timeout" not in kwargs:
            kwargs["timeout"] = self._timeout
        return super().request(*args, **kwargs)


async def on_request_start(
    session: ClientSession,
    trace_config_ctx: SimpleNamespace,
    params: TraceRequestStartParams,
    # retry_options: ExponentialRetry
) -> None:
    current_attempt = trace_config_ctx.trace_request_ctx["current_attempt"]
    print(f"attempt {current_attempt -1}")
    # if retry_options.attempts <= current_attempt:
    #     logger.warning("Wow! We are in last attempt")


def flatten(t):
    return [item for sublist in t for item in sublist]


class _DataSource(object):
    @staticmethod
    def map():
        raise NotImplementedError

    def __init__(self, ID: str):
        self.ID = ID
        self.URL = ""
        self.progress: bool = True

    def _increment_progress(self, task=None):
        if self.progress:
            self.bar.update(1)

    def _init_progress(self, totalDuration):
        if self.progress and not hasattr(self, "bar"):
            self.bar = tqdm(total=totalDuration)

    def _update_progress_description(self, description):
        if self.progress:
            self.bar.set_description(description)

    def _close_progress(self):
        if self.progress:
            self.bar.close()
            del self.bar

    @contextmanager
    def session_with_retries(self, timeout=10, retries=None):
        """Context manager for creating a session with timeout and retry adapters."""
        if retries is None:
            retries = sync_retries

        session = SessionWithTimeout(timeout=timeout)
        session.mount("http://", HTTPAdapter(max_retries=retries))
        session.mount("https://", HTTPAdapter(max_retries=retries))

        try:
            yield session
        finally:
            session.close()

    def request_dataframe(
        self,
        start: datetime_like,
        end: datetime_like,
        process_data: bool = True,
        parallel: bool = False,
        progress: bool = True,
        timeout: int = 20,
        **kwargs,
    ) -> pd.DataFrame:
        self.progress = progress

        if parallel:
            data = async_runner(
                self._async_request_dataframe,
                start,
                end,
                process_data,
                timeout=timeout,
                **kwargs,
            )

        # if not running async
        else:
            data = self._sync_request_dataframe(
                start, end, process_data, timeout=timeout, **kwargs
            )

        return data

    def _request_url(
        self,
        start: datetime_like,
        end: datetime_like,
        datatype: Union[str, Sequence[str]],
    ) -> Any:
        return NotImplementedError

    def _sync_request_dataframe(
        self,
        start: datetime_like,
        end: datetime_like,
        process_data: bool,
        pull_freq: str,
        timeout: int = 20,
    ) -> pd.DataFrame:
        raise NotImplementedError

    def _sync_request_data_series(
        self,
        start: datetime_like,
        end: datetime_like,
        pull_freq: str = "YS",
        timeout: int = 20,
        **kwargs,
    ) -> pd.DataFrame:
        # convert string inputs to datetime-like
        dStart = pd.to_datetime(start)
        dEnd = pd.to_datetime(end)

        # yearly pulls from start of year
        # was getting some weird API behaviour when given
        # requesting date ranges that span the new year
        # freq = "AS"

        # set up annual date range, appending start date which may not be Jan 1
        dRange = pd.date_range(dStart, dEnd, freq=pull_freq).insert(0, dStart)
        # append end date, which may not be Jan 1 and drop dups in case it was
        dRange = dRange.insert(len(dRange), dEnd).drop_duplicates()
        self._init_progress(totalDuration=len(dRange) - 1)
        self._update_progress_description("Downloading")
        with self.session_with_retries(timeout=timeout) as session:
            data = []
            for i in range(len(dRange) - 1):
                data.append(
                    self._sync_request_data(
                        start=dRange[i],
                        end=dRange[i + 1] - pd.Timedelta("1 minute"),
                        session=session,
                        **kwargs,
                    )
                )
                self._increment_progress()
        return data

    def _sync_request_data(
        self, start: datetime_like, end: datetime_like, session: Session
    ) -> Union[ndarray, str, List[dict]]:
        raise NotImplementedError

    async def _async_request_dataframe(
        self,
        start: datetime_like,
        end: datetime_like,
        process_data: bool,
        pull_freq: str,
        conn_limit: int,
        retry_options: RetryOptionsBase,
        timeout: int = 20,
    ) -> pd.DataFrame:
        raise NotImplementedError

    async def _async_request_data_series(
        self,
        start: datetime_like,
        end: datetime_like,
        pull_freq: str = "YS",
        conn_limit: int = 7,
        retry_options: RetryOptionsBase = async_retries,
        timeout: int = 20,
        **kwargs,
    ) -> pd.DataFrame:
        # convert string inputs to datetime-like
        dStart = pd.to_datetime(start)
        dEnd = pd.to_datetime(end)

        # yearly pulls from start of year
        # was getting some weird API behaviour when given
        # requesting date ranges that span the new year
        # set up annual date range, appending start date which may not be Jan 1
        dRange = pd.date_range(dStart, dEnd, freq=pull_freq).insert(0, dStart)
        # append end date, which may not be Jan 1 and drop dups in case it was
        dRange = dRange.insert(len(dRange), dEnd).drop_duplicates()

        self._init_progress(len(dRange) - 1)
        # set up request session
        async with TCPConnector(limit=conn_limit) as connector:
            client_timeout = ClientTimeout(total=timeout)
            # trace_config = TraceConfig()
            # trace_config.on_request_start.append(on_request_start)
            async with ClientSession(
                connector=connector,
                timeout=client_timeout,
                # trace_configs=[trace_config],
            ) as client_session:

                async with RetryClient(
                    client_session=client_session,
                    retry_options=retry_options,
                ) as session:
                    # create async tasks
                    # https://docs.python.org/3/library/asyncio-task.html#creating-tasks
                    tasks = [
                        asyncio.ensure_future(
                            self._async_request_data(
                                start=dRange[i],
                                end=dRange[i + 1] - pd.Timedelta("1 minute"),
                                session=session,
                                **kwargs,
                            )
                        )
                        for i in range(len(dRange) - 1)
                    ]
                    for task in tasks:
                        task.add_done_callback(self._increment_progress)
                    # run tasks concurrently and return list of responses
                    # https://docs.python.org/3/library/asyncio-task.html#running-tasks-concurrently
                    self._update_progress_description("Downloading")
                    return await asyncio.gather(*tasks)

    async def _async_request_data(
        self, start: datetime_like, end: datetime_like, session: RetryClient
    ) -> Union[ndarray, str, List[dict]]:
        raise NotImplementedError
