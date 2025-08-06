import os
from typing import Any, Dict, List, Optional, TypeVar

import httpx

from .__version__ import __version__, __title__, __host__


T = TypeVar("T", bound="BaseAsyncClient")
USER_AGENT = "python-%s/%s" % (__title__, __version__)
TOKEN_NAME = "%s_TOKEN" % __title__.upper()
HOST_NAME = "%s_HOST" % __title__.upper()


class BaseClient:
    def __init__(
        self,
        token: Optional[str] = None,
        timeout: Optional[float] = 10,
        host: Optional[str] = "",
    ):
        if token is None:
            token = os.getenv(TOKEN_NAME)
        assert (
            token is not None
        ), f"Token not found. Use Client(token='<token>') or set env {TOKEN_NAME}=<token>"
        self._url = f"https://{host or os.getenv(HOST_NAME) or __host__}"
        self._version = __version__
        self._token = token
        self._timeout = timeout
        self._user_agent = USER_AGENT
        self._headers = {
            "accept": "application/json",
            "user-agent": self._user_agent,
            "x-access-key": token,
        }


class BaseSyncClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = httpx.Client(base_url=self._url, timeout=self._timeout)
        self._client.headers.update(self._headers)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        if params:
            params = {k: v for k, v in params.items() if v}
        resp = self._client.request(
            method,
            path,
            headers=self._headers | (headers or {}),
            params=params,
            data=data,
            json=json,
            timeout=self._timeout,
        )
        if "json" in resp.headers.get("content-type", "").lower():
            return resp.json()
        return resp.content

    def _paging_request(
        self,
        path: str,
        params: Optional[Dict[str, Any]],
        count: Optional[int] = None,
        container: Optional[List[Dict]] = None,
        page_key: str = "page_id",
        max_requests: Optional[int] = None,
        skip_duplicates: bool = True,
        response_key: Optional[str] = "items",
    ) -> List[Dict]:
        if params is None:
            params = {}
        if container is None:
            container = []
        work_count = 0
        request_count = 0
        pks = set()
        while True:
            res = self._request("GET", path, params=params)
            request_count += 1
            if isinstance(res, list) and len(res) == 2:
                items, npid = res
            else:
                items = res["response"].get(response_key)
                npid = res.get("next_page_id")
            if count is not None:
                rest = count - work_count
                items = items[:rest]
            if skip_duplicates:
                items2 = []
                for item in items:
                    pk = item["pk"]
                    if pk in pks:
                        continue
                    items2.append(item)
                    pks.add(pk)
                items = items2
            container.extend(items)
            work_count += len(items)
            if not npid:
                break
            if count is not None and work_count == count:
                break
            if max_requests is not None and max_requests >= request_count:
                break
            params[page_key] = npid
        return container


class BaseAsyncClient(BaseClient):
    def __init__(self, token: Optional[str] = None, timeout: Optional[float] = 10):
        super().__init__(token=token, timeout=timeout)
        self._client = httpx.AsyncClient(base_url=self._url, timeout=self._timeout)
        self._client.headers.update(self._headers)

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict:
        if params:
            params = {k: v for k, v in params.items() if v}
        resp = await self._client.request(
            method,
            path,
            headers=self._headers | (headers or {}),
            params=params,
            data=data,
            json=json,
            timeout=self._timeout,
        )
        if "json" in resp.headers.get("content-type", "").lower():
            return resp.json()
        return resp.content

    async def _paging_request(
        self,
        path: str,
        params: Optional[Dict[str, Any]],
        count: Optional[int] = None,
        container: Optional[List[Dict]] = None,
        page_key: str = "page_id",
        response_key: Optional[str] = "items",
        max_requests: Optional[int] = None,
        skip_duplicates: bool = True,
    ) -> List[Dict]:
        if params is None:
            params = {}
        if container is None:
            container = []
        work_count = 0
        request_count = 0
        pks = set()
        while True:
            res = await self._request("GET", path, params=params)
            request_count += 1
            if isinstance(res, list) and len(res) == 2:
                items, npid = res
            else:
                items = res["response"].get(response_key)
                npid = res.get("next_page_id")
            if count is not None:
                rest = count - work_count
                items = items[:rest]
            if skip_duplicates:
                items2 = []
                for item in items:
                    pk = item["pk"]
                    if pk in pks:
                        continue
                    items2.append(item)
                    pks.add(pk)
                items = items2
            container.extend(items)
            work_count += len(items)
            if not npid:
                break
            if count is not None and work_count == count:
                break
            if max_requests is not None and max_requests >= request_count:
                break
            params[page_key] = npid
        return container

    async def aclose(self) -> None:
        """
        Close client.
        """
        await self._client.aclose()

    async def __aenter__(self: T) -> T:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self._client.__aexit__(*args)
