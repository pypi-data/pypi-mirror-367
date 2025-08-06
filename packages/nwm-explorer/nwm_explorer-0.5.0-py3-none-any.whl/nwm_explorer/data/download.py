"""Utilities to support downloading files."""
from typing import Callable
from time import sleep
from pathlib import Path
import asyncio
import aiohttp.client_exceptions
from yarl import URL
import aiohttp
from aiohttp.typedefs import LooseHeaders
import aiofiles
import ssl
from http import HTTPStatus
import warnings
import inspect

from nwm_explorer.logging.logger import get_logger

def default_file_validator(filepath: Path) -> None:
    """
    Validate that given filepath opens and closes without raising.

    Parameters
    ----------
    filepath: Path
        Path to file.
    
    Returns
    -------
    None
    """
    fo = filepath.open("rb")
    fo.close()

async def download_file_awaitable(
        url: str | URL,
        filepath: str | Path,
        session: aiohttp.ClientSession,
        chunk_size: int = 1024,
        overwrite: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        timeout: int = 300
        ) -> None:
    """
    Retrieve a single file from url and save to filepath.
    
    Parameters
    ----------
    url: str | URL, required
        Source URL to download.
    filepath: str | Path, required
        Destination to save file.
    session: ClientSession, required
        Session object used for retrieval.
    chunk_size: int, optional, default 1024
        Amount of data to write at a time (KB).
    overwrite: bool, optional, default False
        If filepath exists, overwrite if True, else skip download.
    ssl_context: SSLContext, optional
        SSL configuration object. Uses system defaults unless otherwise
        specified.
    timeout: int, optional, default 300
        Maximum number of seconds to wait for a response to return.
        
    Returns
    -------
    None
    """
    # Check for file existence
    if not overwrite and Path(filepath).exists():
        message = f"File exists, skipping download of {filepath}"
        warnings.warn(message, UserWarning)
        return

    # SSL
    if ssl_context is None:
        ssl_context = ssl.create_default_context()

    # Fetch
    async with session.get(url, ssl=ssl_context, timeout=timeout) as response:
        # Warn if unable to locate
        if response.status == HTTPStatus.SERVICE_UNAVAILABLE:
            status = HTTPStatus(response.status)
            message = (
                f"HTTP Status: {status.value}" + 
                f" - {status.phrase}" + 
                f" - {status.description}\n" + 
                f"{response.url}"
                )
            raise RuntimeError(message)

        # Warn if unable to locate
        if response.status != HTTPStatus.OK:
            status = HTTPStatus(response.status)
            message = (
                f"HTTP Status: {status.value}" + 
                f" - {status.phrase}" + 
                f" - {status.description}\n" + 
                f"{response.url}"
                )
            warnings.warn(message, RuntimeWarning)
            return

        # Stream download
        async with aiofiles.open(filepath, 'wb') as fo:
            while True:
                chunk = await response.content.read(chunk_size)
                if not chunk:
                    break
                await fo.write(chunk)

async def download_files_awaitable(
        *src_dst: tuple[str | URL, str | Path],
        auto_decompress: bool = True,
        headers: LooseHeaders | None = None,
        limit: int = 100,
        chunk_size: int = 1024,
        overwrite: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        timeout: int = 300
        ) -> None:
    """
    Asynchronously retrieve multiple files from urls and save to filepaths.
    
    Parameters
    ----------
    *src_dst: tuple[str | Path, str | URL], required
        One or more tuples containing two values. The first value is the 
        source URL from which to retrieve a file, the second value is the
        filepath where the file will be saved.
    auto_decompress: bool, optional, default True
        Automatically decompress responses.
    headers: LooseHeaders | None, default None
        Additional headers to send with each request.
    limit: int, optional, default 100
        Maximum number of simultaneous connections.
    chunk_size: int, optional, default 1024
        Amount of data to write at a time (KB).
    overwrite: bool, optional, default False
        If filepath exists, overwrite if True, else skip download.
    ssl_context: SSLContext, optional
        SSL configuration object. Uses system defaults unless otherwise
        specified.
    timeout: int, optional, default 300
        Maximum number of seconds to wait for a response to return.
    
    Returns
    -------
    None
    """
    # SSL
    if ssl_context is None:
        ssl_context = ssl.create_default_context()

    # Retrieve
    connector = aiohttp.TCPConnector(limit=limit)
    async with aiohttp.ClientSession(
        connector=connector,
        headers=headers,
        auto_decompress=auto_decompress
        ) as session:
        await asyncio.gather(*(
            download_file_awaitable(
                url,
                filepath,
                session,
                chunk_size=chunk_size,
                overwrite=overwrite,
                ssl_context=ssl_context,
                timeout=timeout
                ) for (url, filepath) in src_dst
        ))

def download_files(
        *src_dst: tuple[str | URL, str | Path],
        auto_decompress: bool = True,
        headers: LooseHeaders | None = None,
        limit: int = 100,
        chunk_size: int = 1024,
        overwrite: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        timeout: int = 300,
        file_validator: Callable[[Path], None] = default_file_validator,
        retries: int = 10
    ) -> None:
    """
    Asynchronously retrieve multiple files from urls and save to filepaths.
    
    Parameters
    ----------
    *src_dst: tuple[str | Path, str | URL], required
        One or more tuples containing two values. The first value is the 
        source URL from which to retrieve a file, the second value is the
        filepath where the file will be saved.
    auto_decompress: bool, optional, default True
        Automatically decompress responses.
    headers: LooseHeaders | None, default None
        Additional headers to send with each request.
    limit: int, optional, default 100
        Maximum number of simultaneous connections.
    chunk_size: int, optional, default 1024
        Amount of data to write at a time (KB).
    overwrite: bool, optional, default False
        If filepath exists, overwrite if True, else skip download.
    ssl_context: SSLContext, optional
        SSL configuration object. Uses system defaults unless otherwise
        specified.
    timeout: int, optional, default 300
        Maximum number of seconds to wait for a response to return.
    file_validator: Callable, optional
        Function used to validate files.
    
    Returns
    -------
    None

    Examples
    --------
    >>> # This will download the pandas and numpy homepages and save them to 
    >>> # ./pandas_index.html and ./numpy_index.html
    >>> from download import download_files
    >>> download_files(
    ...     ("https://pandas.pydata.org/docs/user_guide/index.html", "pandas_index.html"),
    ...     ("https://numpy.org/doc/stable/index.html", "numpy_index.html")
    ...     )
    """
    # Get logger
    name = __loader__.name + "." + inspect.currentframe().f_code.co_name
    logger = get_logger(name)

    # SSL
    if ssl_context is None:
        ssl_context = ssl.create_default_context()

    # Retrieve
    for attempt in range(retries):
        logger.info(f"Downloading files, attempt {attempt}")
        try:
            asyncio.run(
                download_files_awaitable(
                    *src_dst,
                    auto_decompress=auto_decompress,
                    headers=headers,
                    limit=limit,
                    chunk_size=chunk_size,
                    overwrite=overwrite,
                    ssl_context=ssl_context,
                    timeout=timeout
                    )
                )
        except aiohttp.client_exceptions.ServerDisconnectedError:
            warnings.warn("Server error, trying again", RuntimeWarning)
        except RuntimeError as e:
            warnings.warn(str(e), RuntimeWarning)
            warnings.warn("Server error, trying again", RuntimeWarning)
        except asyncio.TimeoutError:
            warnings.warn("Timeout error, trying again", RuntimeWarning)
        except aiohttp.client_exceptions.ClientPayloadError:
            warnings.warn("Failed to write file, trying again", RuntimeWarning)

        # Validate files
        logger.info("Validating files, this will take some time")
        filepaths = [Path(dst) for _, dst in src_dst]
        validated = 0
        for fp in filepaths:
            logger.info(f"{fp}")
            if fp.exists():
                try:
                    file_validator(fp)
                    validated += 1
                except:
                    fp.unlink()
                    break
            else:
                break
        if validated == 0:
            warnings.warn("Unable to retrieve any files", RuntimeWarning)
        if validated == len(filepaths):
            logger.info("All files validated")
            return
        warnings.warn("Unable to retrieve all files, trying again", RuntimeWarning)
        sleep(5 * 2 ** attempt)
    warnings.warn("Unable to retrieve all files", RuntimeWarning)
