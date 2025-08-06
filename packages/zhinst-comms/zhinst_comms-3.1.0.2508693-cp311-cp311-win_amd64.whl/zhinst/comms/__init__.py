import typing
import urllib.parse
from ._comms import *
from ._comms.errors import BadRequestError, BaseError, TimeoutError
import aiohttp
import asyncio
import re

__doc__ = _comms.__doc__
__version__ = _comms.__version__
__commit_hash__ = _comms.__commit_hash__

if hasattr(_comms, "__all__"):
    __all__ = _comms.__all__


async def connect_url(
    self: CapnpContext,
    url: str,
    timeout: int = 1500,
    schema: InterfaceSchema | None = None,
) -> DynamicClient:
    async def do_connect(url: str, allow_redirect: bool):
        # URL in the format host:port, without scheme, is accepted and assumed to be TCP
        if re.fullmatch("[a-zA-Z0-9-.]+:[0-9]+", url):
            url = "tcp://" + url
        # We check the scheme manually because the scheme inferred by the url parsing
        # can be confusing also in seemingly benign cases. For example, the scheme of
        # "127.0.0.1:8080" is "127.0.0.1"
        if not (url.startswith("http://") or url.startswith("tcp://")):
            raise BadRequestError(
                f"Cannot connect using url {url}. The url should start with http://, or tcp://"
            )
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme == "tcp":
            parts = parsed_url.netloc.split(":")
            if len(parts) != 2:
                raise BadRequestError(f"Cannot infer host and port from url {url}.")
            try:
                port = int(parts[1])
            except ValueError:
                raise BadRequestError(f"{parts[1]} is not a valid port number.")
            host = parts[0]
            return await self.connect(host, port, timeout, schema)
        if parsed_url.scheme == "http":
            if not allow_redirect:
                raise BaseError(
                    f"Server responded with a redirect for an invalid url: {url}"
                )
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=float(timeout) / 1000)
            ) as session:
                async with session.get(url, allow_redirects=False) as response:
                    if 400 <= response.status < 600:
                        raise BaseError(
                            f"Cannot connect using url {url}. Server responded with error {response.status}."
                        )
                    if response.status not in (300, 301, 302, 303, 307, 308):
                        raise BaseError(
                            f"Url '{url}' points to an HTTP location which is expected to redirect "
                            f"to a capnp server. However, the server did not respond with "
                            f"a valid redirect (returned status code is {response.status})"
                        )
                    location = response.headers.get("Location")
                    if location is None:
                        raise BaseError(
                            f"Cannot connect using url {url}. Server did not report the location of the capnp server."
                        )
            return await do_connect(location, allow_redirect=False)
        raise BadRequestError(
            f"Cannot connect using url {url}. Scheme {parsed_url.scheme} not supported"
        )

    try:
        return await do_connect(url, allow_redirect=True)
    except asyncio.TimeoutError:
        raise TimeoutError("Connection timed out")


_comms.CapnpContext.connect_url = connect_url
