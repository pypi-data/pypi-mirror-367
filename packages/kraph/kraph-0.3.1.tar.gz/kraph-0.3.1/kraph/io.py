from typing import Optional

import aiohttp
from koil import unkoil
from kraph.vars import current_datalayer


async def adownload_file(presigned_url: str, file_name: str, datalayer=None):
    datalayer = datalayer or current_datalayer.get()
    endpoint_url = await datalayer.get_endpoint_url()

    async with aiohttp.ClientSession() as session:
        async with session.get(endpoint_url + presigned_url) as response:
            with open(file_name, "wb") as file:
                while True:
                    chunk = await response.content.read(
                        1024
                    )  # read the response by chunks of 1024 bytes
                    if not chunk:
                        break
                    file.write(chunk)

    return file_name


def download_file(presigned_url: str, file_name: str, datalayer=None):
    return unkoil(
        adownload_file, presigned_url, file_name=file_name, datalayer=datalayer
    )
