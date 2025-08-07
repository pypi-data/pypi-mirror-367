import asyncio

from kraph.scalars import RemoteUpload
from rath.links.parsing import ParsingLink
from rath.operation import Operation, opify
from typing import Any, Optional

from pydantic import Field
from concurrent.futures import ThreadPoolExecutor
import uuid
from functools import partial
from kraph.datalayer import DataLayer
from typing import TYPE_CHECKING
import aiohttp
import logging

if TYPE_CHECKING:
    from kraph.api.schema import PresignedPostCredentials


async def aupload_bigfile(
    file: RemoteUpload,
    credentials: "PresignedPostCredentials",
    datalayer: "DataLayer",
    executor: Optional[ThreadPoolExecutor] = None,
) -> str:
    """Store a DataFrame in the DataLayer using presigned post credentials."""

    # Get the endpoint URL
    endpoint_url = await datalayer.get_endpoint_url()

    # Prepare the presigned POST fields
    form_data = {
        "key": credentials.key,
        "x-amz-credential": credentials.x_amz_credential,
        "x-amz-algorithm": credentials.x_amz_algorithm,
        "x-amz-date": credentials.x_amz_date,
        "x-amz-signature": credentials.x_amz_signature,
        "policy": credentials.policy,
    }

    logging.info(f"Uploading file to {endpoint_url} with form data: {form_data}")

    # Use aiohttp for the async POST request with the file as part of form data
    async with aiohttp.ClientSession() as session:
        data = aiohttp.FormData()
        for key, value in form_data.items():
            data.add_field(key, value)
        # Add the file to the form data
        data.add_field("file", file.value, filename=credentials.key)

        try:
            async with session.post(
                endpoint_url + "/" + credentials.bucket,
                data=data,
            ) as response:
                # Check if upload was successful
                if response.status != 204:
                    raise Exception(f"Failed to upload file: {response.status}")

        except aiohttp.ClientError as e:
            raise Exception(f"Upload failed: {e}")

    return credentials.store


async def apply_recursive(func, obj, typeguard):
    """
    Recursively applies an asynchronous function to elements in a nested structure.

    Args:
        func (callable): The asynchronous function to apply.
        obj (any): The nested structure (dict, list, tuple, etc.) to process.
        typeguard (type): The type of elements to apply the function to.

    Returns:
        any: The nested structure with the function applied to elements of the specified type.
    """
    if isinstance(
        obj, dict
    ):  # If obj is a dictionary, recursively apply to each key-value pair
        return {k: await apply_recursive(func, v, typeguard) for k, v in obj.items()}
    elif isinstance(obj, list):  # If obj is a list, recursively apply to each element
        return await asyncio.gather(
            *[apply_recursive(func, elem, typeguard) for elem in obj]
        )
    elif isinstance(
        obj, tuple
    ):  # If obj is a tuple, recursively apply to each element and convert back to tuple
        return tuple(
            await asyncio.gather(
                *[apply_recursive(func, elem, typeguard) for elem in obj]
            )
        )
    elif isinstance(obj, typeguard):  # If obj matches the typeguard, apply the function
        return await func(obj)
    else:  # If obj is not a dict, list, tuple, or matching the typeguard, return it as is
        return obj


class UploadLink(ParsingLink):
    """Data Layer Upload Link

    This link is used to upload  supported types to a DataLayer.
    It parses queries, mutatoin and subscription arguments and
    uploads the items to the DataLayer, and substitures the
    DataFrame with the S3 path.

    Args:
        ParsingLink (_type_): _description_


    """

    datalayer: DataLayer
    executor: ThreadPoolExecutor = Field(
        default_factory=lambda: ThreadPoolExecutor(max_workers=4), exclude=True
    )
    _executor_session: Any = None

    async def __aenter__(self):
        self._executor_session = self.executor.__enter__()

    async def aget_credentials(self, key, datalayer) -> Any:
        from kraph.api.schema import RequestUploadMutation

        operation = opify(
            RequestUploadMutation.Meta.document,
            variables={"input": {"key": key, "datalayer": datalayer}},
        )

        async for result in self.next.aexecute(operation):
            return RequestUploadMutation(**result.data).request_upload

    async def aupload_remote(self, datalayer: "DataLayer", file: RemoteUpload) -> str:
        assert datalayer is not None, "Datalayer must be set"
        endpoint_url = await datalayer.get_endpoint_url()

        credentials = await self.aget_credentials(file.key, endpoint_url)
        return await aupload_bigfile(
            file,
            credentials,
            datalayer,
            self._executor_session,
        )

    async def aparse(self, operation: Operation) -> Operation:
        """Parse the operation (Async)

        Extracts the DataFrame from the operation and uploads it to the DataLayer.

        Args:
            operation (Operation): The operation to parse

        Returns:
            Operation: _description_
        """

        datalayer = operation.context.kwargs.get("datalayer", self.datalayer)

        operation.variables = await apply_recursive(
            partial(self.aupload_remote, datalayer), operation.variables, RemoteUpload
        )

        return operation

    async def adisconnect(self):
        self.executor.__exit__(None, None, None)
