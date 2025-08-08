"""REST client handling, including canvasStream base class."""

import requests
from urllib import parse
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable

from memoization import cached

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class CanvasStream(RESTStream):
    """canvas stream class."""

    def __init__(self, tap=None, name=None, schema=None, path=None, **kwargs):
        """Initialize stream with record limit tracking."""
        self._direct_config = kwargs.pop('config', None)
        
        super().__init__(tap=tap, name=name, schema=schema, path=path, **kwargs)
        
        self._record_limit = self.config.get("record_limit")
        self._records_count = 0

    @property
    def config(self) -> dict:
        """Get configuration, preferring direct config for testing."""
        if self._direct_config is not None:
            return self._direct_config
        return super().config if hasattr(super(), 'config') else self._tap.config

    @property
    def url_base(self) -> str:
        """Return the base URL for the Canvas API."""
        return self.config["base_url"]

    records_jsonpath = "$[*]"  
    next_page_token_jsonpath = "$.next_page"  

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object."""
        return BearerTokenAuthenticator.create_for_stream(
            self, token=self.config.get("api_key")
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        if self._record_limit is not None and self._records_count >= self._record_limit:
            return None

        next_page_dict = response.links.get("next", None)
        if next_page_dict:
            next_page = next_page_dict["url"]
            query = dict(parse.parse_qsl(parse.urlsplit(next_page).query))
            next_page_token = query["page"]
        else:
            next_page_token = None

        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        params["per_page"] = 100
        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        for row in extract_jsonpath(self.records_jsonpath, input=response.json()):
            if (
                self._record_limit is not None
                and self._records_count >= self._record_limit
            ):
                break
            self._records_count += 1
            yield row
