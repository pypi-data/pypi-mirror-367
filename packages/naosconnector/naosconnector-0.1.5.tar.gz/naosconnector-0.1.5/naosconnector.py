"""
naos_connector.py
This module contains the NaosConnector class which is used to connect to a Naos platform.
"""

from __future__ import annotations

__author__ = "Nicolas Parment"
__copyright__ = "Copyright 2024, Forsk"
__credits__ = ["Nicolas Parment"]
__license__ = "Commercial"
__version__ = "0.1.5"
__maintainer__ = "Nicolas Parment"
__email__ = "nparment@forsk.com"
__status__ = "Development"


import os
import logging

import functools
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, Optional, Tuple, Union
from urllib.parse import urlparse, urljoin
import threading

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry

# logger
LOGGING_LEVEL = getattr(logging, os.getenv("LOGGING_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(
    level=LOGGING_LEVEL,
    format="%(asctime)s [%(levelname)-5.5s]: %(message)s",
    handlers=[
        logging.StreamHandler()
])
logging.getLogger('charset_normalizer').disabled = True
logger = logging.getLogger(__name__)


class NaosConnectorError(Exception):
    """Base exception class for NaosConnector."""
    pass


class AuthenticationError(NaosConnectorError):
    """Exception raised for authentication failures."""
    pass


class Decorators:
    """
    Class containing Decorators for NaosConnector methods.
    """

    @staticmethod
    def http_exception_handler(func):
        """
        Decorator for get/post/put/delete exceptions
        """
        @functools.wraps(func)
        def inner_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as err:
                logger.debug(err)
                logger.debug(err.response.text)
                raise
        return inner_function

    @staticmethod
    def autorefresh_token(func):
        """
        Decorator for access token refresh and 401 error handling
        """
        @functools.wraps(func)
        def inner_function(naos_connector, *args, **kwargs):
            if naos_connector.get_tokens():
                if datetime.now(timezone.utc) + timedelta(seconds=30) > naos_connector.access_token_expiration:
                    naos_connector.refresh_access_token()
            try:
                return func(naos_connector, *args, **kwargs)
            except requests.exceptions.HTTPError as err:
                if err.response.status_code == 401:
                    logger.warning("Received 401 error. Attempting to refresh token.")
                    naos_connector.refresh_access_token()
                    return func(naos_connector, *args, **kwargs)
                raise
        return inner_function


class NaosConnector:
    """
    Class for connecting to a Naos platform.
    Manages connections, authentication (tokens), and REST API calls.
    """

    DEFAULT_CONNECT_TIMEOUT: int = 10
    DEFAULT_READ_TIMEOUT: int = 600
    DEFAULT_MAX_RETRIES: int = 10
    DEFAULT_BACKOFF_FACTOR: float = 0.1
    DEFAULT_POOL_MAXSIZE: int = 10

    def __init__(
        self,
        server: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        protocol: str = 'https',
        proxies: Optional[Dict[str, str]] = None,
        tokens: Optional[Dict[str, Any]] = None,
        pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
        read_timeout: int = DEFAULT_READ_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    ):
        """
        Initializes Naos server connection parameters and session.

        :param server: Naos Gateway server in the format 'protocol://host:port'.
        :param host: Naos Gateway host.
        :param port: Naos Gateway port.
        :param protocol: Protocol to use (default is 'https').
        :param proxies: Proxy configuration dictionary.
        :param tokens: Authentication tokens.
        :param pool_maxsize: Maximum size of the connection pool.
        :param connect_timeout: Connection timeout in seconds.
        :param read_timeout: Read timeout in seconds.
        :param max_retries: Maximum number of retries for failed requests.
        :param backoff_factor: Backoff factor for retries.
        """
        if server:
            parsed_url = urlparse(server)
            if not parsed_url.scheme or not parsed_url.hostname or not parsed_url.port:
                raise ValueError("Server must be in the format 'protocol://host:port'")
            self._protocol = parsed_url.scheme
            self._host = parsed_url.hostname
            self._port = parsed_url.port
            self.base_url = f"{self._protocol}://{self._host}:{self._port}"
        elif host and port:
            self._host = host
            self._port = port
            self.base_url = f"{protocol}://{self._host}:{self._port}"
        else:
            raise ValueError("Either 'server' or both 'host' and 'port' must be provided.")

        self._lock = threading.Lock()
        self.tokens: Dict[str, Any] = tokens if tokens else {}
        self.access_token_expiration: Optional[datetime] = None

        # Initialize session
        self.session: Session = requests.Session()
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout

        # Configure retries
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"]
        )
        adapter = HTTPAdapter(max_retries=retries, pool_maxsize=pool_maxsize, pool_block=True)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        # Set proxies if provided
        if proxies:
            self.session.proxies.update(proxies)

        # Set authorization header if tokens are provided
        if self.tokens.get("access_token"):
            self.session.headers.update({'Authorization': f'Bearer {self.tokens["access_token"]}'})
            access_token_exp = self.tokens.get("access_token_expiration")
            if access_token_exp is not None:
                self.access_token_expiration = datetime.fromtimestamp(access_token_exp)
            else:
                self.access_token_expiration = None

    def get_host(self) -> str:
        """Returns the Naos Engine Host."""
        return self._host

    def get_port(self) -> int:
        """Returns the Naos Engine Port."""
        return self._port

    def get_tokens(self) -> Dict[str, Any]:
        """Returns tokens information."""
        return self.tokens

    def _format_url(self, path: str) -> str:
        """
        Forms a complete URL based on the base_url and the provided path.

        :param path: API endpoint path or full URL.
        :return: Complete URL.
        """
        if path.lower().startswith('http'):
            return path
        return urljoin(f"{self.base_url}/", path.lstrip('/'))

    def _is_token_expiring(self) -> bool:
        """
        Checks if the access token is about to expire within the next 30 seconds.

        :return: True if token is expiring soon, False otherwise.
        """
        if not self.access_token_expiration:
            return False
        return datetime.now(timezone.utc) + timedelta(seconds=30) > self.access_token_expiration

    def _refresh_token(self) -> bool:
        """
        Refreshes the access token using the refresh token.

        :return: True if refresh was successful, False otherwise.
        """
        with self._lock:

            url = 'v1/auth/token'

            if not self.tokens.get('refresh_token'):
                logger.error("No refresh token available.")
                return False

            self.session.headers['Authorization'] = f'Bearer {self.tokens["refresh_token"]}'
            url = self._format_url(url)

            try:
                response = self.session.post(url=url, timeout=(self.connect_timeout, self.read_timeout))
                response.raise_for_status()
                data = response.json()
                self.tokens['access_token'] = data['access_token']
                self.access_token_expiration = datetime.now(timezone.utc) + timedelta(seconds=data.get('access_token_expires_in'))
                self.session.headers['Authorization'] = f'Bearer {self.tokens["access_token"]}'
                logger.debug("Tokens refreshed")

            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to refresh tokens: {e}")


            return True


    @Decorators.autorefresh_token
    @Decorators.http_exception_handler
    def get(self, path: str, **kwargs) -> Response:
        """Performs a GET request."""
        response = self.session.get(self._format_url(path), timeout=(self.connect_timeout, self.read_timeout), **kwargs)
        response.raise_for_status()
        return response

    @Decorators.autorefresh_token
    @Decorators.http_exception_handler
    def put(self, path: str, **kwargs) -> Response:
        """Performs a PUT request."""
        response = self.session.put(self._format_url(path), timeout=(self.connect_timeout, self.read_timeout), **kwargs)
        response.raise_for_status()
        return response

    @Decorators.autorefresh_token
    @Decorators.http_exception_handler
    def post(self, path: str, **kwargs) -> Response:
        """Performs a POST request."""
        response = self.session.post(self._format_url(path), timeout=(self.connect_timeout, self.read_timeout), **kwargs)
        response.raise_for_status()
        return response

    @Decorators.autorefresh_token
    @Decorators.http_exception_handler
    def patch(self, path: str, **kwargs) -> Response:
        """Performs a PATCH request."""
        response = self.session.patch(self._format_url(path), timeout=(self.connect_timeout, self.read_timeout), **kwargs)
        response.raise_for_status()
        return response

    @Decorators.autorefresh_token
    @Decorators.http_exception_handler
    def delete(self, path: str, **kwargs) -> Response:
        """Performs a DELETE request."""
        response = self.session.delete(self._format_url(path), timeout=(self.connect_timeout, self.read_timeout), **kwargs)
        response.raise_for_status()
        return response

    def basic_auth(self, login: str, password: str) -> Response:
        """
        Logs in using Basic Authentication.

        :param login: Username.
        :param password: Password.
        :return: Response object.
        """
        url = 'v1/auth/login'
        url = self._format_url(url)
        try:
            response = self.session.post(url=url, auth=(login, password))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate: {e}")
            raise AuthenticationError("Failed to authenticate.")

        data = response.json()
        self.tokens['access_token'] = data['access_token']
        self.access_token_expiration = datetime.now(timezone.utc) + timedelta(seconds=data.get('access_token_expires_in'))
        self.tokens['refresh_token'] = data['refresh_token']

        self.session.headers.update({'Authorization': f'Bearer {self.tokens["access_token"]}'})
        logger.debug("Basic Authentication succeeded.")
        return response

    def refresh_access_token(self) -> Response:
        """
        Refreshes the access token using the refresh token.

        :return: Response object.
        """
        if not self._refresh_token():
            raise AuthenticationError("Failed to refresh access token.")
        return Response()  # Placeholder: Modify based on actual implementation if needed.

    def close(self) -> None:
        """Closes the session."""
        self.session.close()
        logger.debug("Session closed.")

    def __enter__(self) -> NaosConnector:
        """Enters the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exits the runtime context and closes the session."""
        self.close()
