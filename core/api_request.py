import enum
import logging
from typing import Dict
import aiohttp
from core.config import settings
from requests.auth import HTTPBasicAuth

from schemas.entities import APIRequest

logger = logging.getLogger()


class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthz") == -1

# logging.getLogger("uvicorn.access").addFilter(EndpointFilter())


class RequestMethod(str, enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


async def client(
    url: str,
    method: RequestMethod,
    payload: Dict,
    headers=None,
    username: str = None,
    password: str = None,
    timeout: int = 30,
    *args,
    **kwargs,
) -> APIRequest:
    """
    this method sent request using aiohttp client session for others APIS
    Arguments:
        url: url to send request
        method: http method the methods can be get post put or delete
        payload: dict with data to send for other APIS
        headers: dict with headers to send in your request
        verify_ssl: true or false to check ssl or not
        timeout: the limit in seconds
    Return:
        APIRequests
    """

    if headers is None:
        headers = {}

    request_parameters = {}

    # logger.info(f"using payload : {payload} in request")

    request_parameters["data"] = payload
    request_parameters["headers"] = headers
    request_parameters["timeout"] = timeout

    if username and password:
        request_parameters["auth"] = aiohttp.BasicAuth(username, password)

    request_parameters = {**request_parameters, **kwargs}

    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.post(url, **request_parameters) as resp:
            # logger.info(f"end request api method: {method} url: {url}")
            data = await resp.read()
            dict_str = data.decode("UTF-8")
            return APIRequest(
                status_code=resp.status, payload=data, text=dict_str
            )
