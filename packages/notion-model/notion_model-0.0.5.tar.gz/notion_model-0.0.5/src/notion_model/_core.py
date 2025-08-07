from __future__ import annotations

from os import environ
from typing import Any, Literal, TypedDict, TypeVar, overload

import aiohttp
import requests
from pydantic import TypeAdapter

from . import _types as types

NOTION_VERSION = "2022-06-28"
SYNC_TIMEOUT = 10  # seconds
ASYNC_TIMEOUT = aiohttp.ClientTimeout(
    total=30,  # Total request timeout
    connect=10,  # Connection establishment timeout
    sock_read=20,  # Socket read timeout
)
MAX_PAGE_SIZE = 100
T_Block = TypeVar("T_Block", bound=types.NotionBlock)

ERROR_DESCRIPTIONS: dict[tuple[int, str], str] = {
    (400, "invalid_json"): "The request body could not be decoded as JSON.",
    (400, "invalid_request_url"): "The request URL is not valid.",
    (400, "invalid_request"): "This request is not supported.",
    (
        400,
        "invalid_grant",
    ): "The provided authorization grant (e.g., authorization code, resource owner credentials) or refresh token is invalid, expired, revoked, does not match the redirection URI used in the authorization request, or was issued to another client. See OAuth 2.0 documentation for more information.",
    (
        400,
        "validation_error",
    ): "The request body does not match the schema for the expected parameters. Check the 'message' property for more details.",
    (
        400,
        "missing_version",
    ): "The request is missing the required Notion-Version header. See Versioning.",
    (401, "unauthorized"): "The bearer token is not valid.",
    (
        403,
        "restricted_resource",
    ): "Given the bearer token used, the client doesn't have permission to perform this operation.",
    (
        404,
        "object_not_found",
    ): "Given the bearer token used, the resource does not exist. This error can also indicate that the resource has not been shared with owner of the bearer token.",
    (
        409,
        "conflict_error",
    ): "The transaction could not be completed, potentially due to a data collision. Make sure the parameters are up to date and try again.",
    (
        429,
        "rate_limited",
    ): "This request exceeds the number of requests allowed. Slow down and try again. More details on rate limits.",
    (
        500,
        "internal_server_error",
    ): "An unexpected error occurred. Reach out to Notion support.",
    (
        502,
        "bad_gateway",
    ): "Notion encountered an issue while attempting to complete this request (e.g., failed to establish a connection with an upstream server). Please try again.",
    (
        503,
        "service_unavailable",
    ): "Notion is unavailable. This can occur when the time to respond to a request takes longer than 60 seconds, the maximum request timeout. Please try again later.",
    (
        503,
        "database_connection_unavailable",
    ): "Notion's database is unavailable or is not in a state that can be queried. Please try again later.",
    (
        504,
        "gateway_timeout",
    ): "Notion timed out while attempting to complete this request. Please try again later.",
}


def _format_block_id(block_id: str) -> str:
    """Format the block ID to the Notion standard format."""
    """Validate the block ID format."""
    if not isinstance(block_id, str):
        raise ValueError("Block ID must be a string.")

    block_id = block_id.strip()  # Remove leading/trailing whitespace

    if not block_id:
        raise ValueError("Block ID cannot be empty.")

    # Check if the block_id is already in the correct format
    if (
        len(block_id) == 36
        and block_id[8] == "-"
        and block_id[13] == "-"
        and block_id[18] == "-"
        and block_id[23] == "-"
    ):
        return block_id

    # Check if the block_id is a 32-character hexadecimal string
    if len(block_id) == 32:
        try:
            int(block_id, 16)  # Try converting to int base 16
        except ValueError as exe:
            raise ValueError(
                "Block ID must be a 32-character hexadecimal string or a valid UUID."
            ) from exe
    else:
        raise ValueError("Block ID must be a 32-character hexadecimal string or a valid UUID.")

    # If it's a 32-character hexadecimal string, format it
    if "-" not in block_id:
        return (
            f"{block_id[:8]}-{block_id[8:12]}-{block_id[12:16]}-"
            + f"{block_id[16:20]}-{block_id[20:]}"
        )
    return block_id


class RequestBody(TypedDict):
    url: str
    headers: dict[str, str]


class RequestBodyWithParams(RequestBody):
    params: dict[str, Any]


def _error_handler(
    err: requests.exceptions.RequestException | aiohttp.ClientResponseError,
) -> RuntimeError:
    if isinstance(err, requests.exceptions.HTTPError):
        status_code = err.response.status_code
        learn_more = (
            f"Error code is {status_code}, read more at https://developers.notion.com/reference/status-codes#error-codes\n"
            + " Please refer to the Notion API documentation for more details: "
            + "https://developers.notion.com/reference/retrieve-a-block"
        )
        try:
            response_json = err.response.json()
            error_code = response_json.get("code")
            error_description = ERROR_DESCRIPTIONS.get((status_code, error_code))
            message = response_json.get("message")
            if error_description:
                return RuntimeError(
                    f"❌ Notion API Error: {error_description} (Status: {status_code}, "
                    f"Code: {error_code}, Message: {message})"
                )
            else:
                return RuntimeError(
                    f"❌ Error in sync request: {message} (Status: {status_code}, Code: {error_code})"
                )
        except Exception as inner_err:
            raise RuntimeError(f"❌ Error in sync request: {err}." + learn_more) from inner_err
    elif isinstance(err, aiohttp.ClientResponseError):
        status_code = err.status
        error_description = ERROR_DESCRIPTIONS.get((status_code, err.message))
        if error_description:
            return RuntimeError(
                f"❌ Notion API Error: {error_description} (Status: {status_code}, "
                f"Message: {err.message})"
            )
        else:
            return RuntimeError(
                f"❌ Error in async request: {err.message} (Status: {status_code})"
            )
    else:
        return RuntimeError(f"❌ Error in request: {err}.")


class AuthBase:
    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key


class Auth(AuthBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)


class AuthAsync(AuthBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None


class BlocksBase:
    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key

    def _retrieve_a_block_args(self, block_id: str) -> RequestBody:
        return RequestBody(
            url=f"https://api.notion.com/v1/blocks/{_format_block_id(block_id)}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
        )

    def _retrieve_block_children_args(self, block_id: str) -> RequestBodyWithParams:
        return RequestBodyWithParams(
            url=f"https://api.notion.com/v1/blocks/{_format_block_id(block_id)}/children",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
            params={"page_size": MAX_PAGE_SIZE},
        )


class BlocksSync(BlocksBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)

    @overload
    def retrieve_a_block(self, block_id: str) -> types.NotionBlock: ...

    @overload
    def retrieve_a_block(self, block_id: str, block_type: type[T_Block]) -> T_Block: ...

    def retrieve_a_block(self, block_id, block_type=None):
        """Retrieve a block by its ID."""
        args = self._retrieve_a_block_args(block_id)

        try:
            response = requests.get(**args, timeout=SYNC_TIMEOUT)
            response.raise_for_status()
            response_result = response.json()
            if block_type is not None:
                result = block_type.validate_python(response_result)
            else:
                result = TypeAdapter(types.NotionBlock).validate_python(response_result)
            return result
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)

    def retrieve_block_children(self, block_id: str) -> list[types.NotionBlock]:
        """Retrieve the children of a block by its ID."""
        args = self._retrieve_block_children_args(block_id)

        try:
            all_results: list[types.NotionBlock] = []
            has_more, start_cursor = True, None

            while has_more:
                if start_cursor:
                    args["params"]["start_cursor"] = start_cursor

                response = requests.get(**args, timeout=SYNC_TIMEOUT)
                response.raise_for_status()
                response_json = response.json()
                has_more = response_json["has_more"]
                start_cursor = response_json.get("next_cursor")
                all_results += TypeAdapter(list[types.NotionBlock]).validate_python(
                    response_json["results"]
                )
            return all_results

        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class BlocksAsync(BlocksBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None

    @overload
    async def retrieve_a_block(self, block_id: str) -> types.NotionBlock: ...

    @overload
    async def retrieve_a_block(self, block_id: str, block_type: type[T_Block]) -> T_Block: ...

    async def retrieve_a_block(self, block_id, block_type=None):
        """Retrieve a block by its ID."""
        args = self._retrieve_a_block_args(block_id)

        try:
            assert self._session is not None
            async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                response.raise_for_status()
                response_result = await response.json()
                if block_type is not None:
                    result = block_type.validate_python(response_result)
                else:
                    result = TypeAdapter(types.NotionBlock).validate_python(response_result)
                return result
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)

    async def retrieve_block_children(self, block_id: str) -> list[types.NotionBlock]:
        """Retrieve the children of a block by its ID."""
        args = self._retrieve_block_children_args(block_id)

        try:
            assert self._session is not None
            all_results: list[types.NotionBlock] = []
            has_more, start_cursor = True, None

            while has_more:
                if start_cursor:
                    args["params"]["start_cursor"] = start_cursor

                async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                    response.raise_for_status()
                    response_json = await response.json()
                    has_more = response_json["has_more"]
                    start_cursor = response_json.get("next_cursor")

                    all_results += TypeAdapter(list[types.NotionBlock]).validate_python(
                        response_json["results"]
                    )
            return all_results

        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class PagesBase:
    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key

    def _retrieve_a_page_args(
        self, page_id: str, filter_properties: list[str] = []
    ) -> RequestBodyWithParams:
        params = {}
        if filter_properties:
            params["filter_properties"] = filter_properties

        return RequestBodyWithParams(
            url=f"https://api.notion.com/v1/pages/{_format_block_id(page_id)}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
            params=params,
        )


class PagesSync(PagesBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)

    def retrieve_a_page(self, page_id: str, filter_properties: list[str] = []) -> types.Page:
        """Retrieve a page by its ID.

        Args:
            page_id (str): The ID of the page to retrieve.
            filter_properties (list[str], optional): List of property IDs to filter
                in the response. Defaults to [].

        """
        args = self._retrieve_a_page_args(page_id, filter_properties)

        try:
            response = requests.get(**args, timeout=SYNC_TIMEOUT)
            response.raise_for_status()
            response_result = response.json()
            result = TypeAdapter(types.Page).validate_python(response_result)
            return result
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class PagesAsync(PagesBase):
    def __init__(self, notion_api_key: str):
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None

    async def retrieve_a_page(
        self, page_id: str, filter_properties: list[str] = []
    ) -> types.Page:
        """Retrieve a page by its ID."""
        args = self._retrieve_a_page_args(page_id, filter_properties)

        try:
            assert self._session is not None
            async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                response.raise_for_status()
                response_result = await response.json()
                return TypeAdapter(types.Page).validate_python(response_result)
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class DatabasesBase:
    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key

    def _retrieve_a_database_args(self, database_id: str) -> RequestBody:
        return RequestBody(
            url=f"https://api.notion.com/v1/databases/{_format_block_id(database_id)}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
        )


class DatabasesSync(DatabasesBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)

    def retrieve_a_database(self, database_id: str) -> types.Database:
        """Retrieve a database by its ID."""
        args = self._retrieve_a_database_args(database_id)

        try:
            response = requests.get(**args, timeout=SYNC_TIMEOUT)
            response.raise_for_status()
            response_result = response.json()
            result = TypeAdapter(types.Database).validate_python(response_result)
            return result
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class DatabasesAsync(DatabasesBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None

    async def retrieve_a_database(self, database_id: str) -> types.Database:
        """Retrieve a database by its ID."""
        args = self._retrieve_a_database_args(database_id)

        try:
            assert self._session is not None
            async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                response.raise_for_status()
                response_result = await response.json()
                return TypeAdapter(types.Database).validate_python(response_result)
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class CommentsBase:
    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key

    def _retrieve_comments_args(self, block_id: str) -> RequestBodyWithParams:
        return RequestBodyWithParams(
            url=f"https://api.notion.com/v1/comments",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
            params={"block_id": _format_block_id(block_id), "page_size": MAX_PAGE_SIZE},
        )


class CommentsSync(CommentsBase):
    """Class to handle comments in Notion."""

    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)

    def retrieve_comments(self, block_id: str) -> list[types.Comment]:
        """Retrieve comments for a block by its ID."""
        args = self._retrieve_comments_args(block_id)

        try:
            has_more, start_cursor = True, None
            all_results: list[types.Comment] = []
            while has_more:
                if start_cursor:
                    args["params"]["start_cursor"] = start_cursor

                response = requests.get(**args, timeout=SYNC_TIMEOUT)
                response.raise_for_status()
                response_json = response.json()

                has_more = response_json.get("has_more", False)
                start_cursor = response_json.get("next_cursor")

                all_results += TypeAdapter(list[types.Comment]).validate_python(
                    response_json.get("results", [])
                )
            return all_results
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class CommentsAsync(CommentsBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None

    async def retrieve_comments(self, block_id: str) -> list[types.Comment]:
        """Retrieve comments for a block by its ID."""
        args = self._retrieve_comments_args(block_id)

        try:
            assert self._session is not None
            has_more, start_cursor = True, None
            all_results: list[types.Comment] = []

            while has_more:
                if start_cursor:
                    args["params"]["start_cursor"] = start_cursor

                async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                    response.raise_for_status()
                    response_json = await response.json()

                    has_more = response_json.get("has_more", False)
                    start_cursor = response_json.get("next_cursor")

                    all_results += TypeAdapter(list[types.Comment]).validate_python(
                        response_json.get("results", [])
                    )
            return all_results
        except aiohttp.ClientResponseError as e:
            raise _error_handler(e)


class FileUploadsBase:
    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key

    def _retrieve_a_file_upload_args(self, file_id: str) -> RequestBody:
        return RequestBody(
            url=f"https://api.notion.com/v1/file_uploads/{_format_block_id(file_id)}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
        )


class FileUploadsSync(FileUploadsBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)

    def retrieve_a_file_upload(self, file_id: str) -> types.FileUpload:
        """Retrieve a file upload by its ID."""
        args = self._retrieve_a_file_upload_args(file_id)

        try:
            response = requests.get(**args, timeout=SYNC_TIMEOUT)
            response.raise_for_status()
            response_result = response.json()
            result = TypeAdapter(types.FileUpload).validate_python(response_result)
            return result
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class FileUploadsAsync(FileUploadsBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None

    async def retrieve_a_file_upload(self, file_id: str) -> types.FileUpload:
        """Retrieve a file upload by its ID."""
        args = self._retrieve_a_file_upload_args(file_id)

        try:
            assert self._session is not None
            async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                response.raise_for_status()
                response_result = await response.json()
                return TypeAdapter(types.FileUpload).validate_python(response_result)
        except aiohttp.ClientResponseError as e:
            raise _error_handler(e)


class SearchBase:
    class _Sort(TypedDict):
        direction: Literal["ascending", "descending"]
        timestamp: Literal["last_edited_time"]

    class _Filter(TypedDict):
        value: Literal["page", "database"]
        property: Literal["object"]

    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key

    def _search_by_title_args(
        self,
        query: str | None = None,
        sort_obj: SearchBase._Sort | None = None,
        filter_obj: SearchBase._Filter | None = None,
    ) -> RequestBodyWithParams:
        """Build the request body for searching by title."""

        params: dict[str, Any] = {}
        if query:
            params["query"] = query
        if filter_obj:
            params["filter"] = filter_obj
        if sort_obj:
            params["sort"] = sort_obj

        return RequestBodyWithParams(
            url="https://api.notion.com/v1/search",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_VERSION,
            },
            params=params,
        )


class SearchSync(SearchBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)

    def search_by_title(
        self,
        query: str | None = None,
        sort_obj: SearchBase._Sort | None = None,
        filter_obj: SearchBase._Filter | None = None,
        limit: int | None = None,
    ) -> list[types.Database | types.Page]:
        """Search for pages or databases."""
        args = self._search_by_title_args(query, sort_obj, filter_obj)

        try:
            has_more, start_cursor = True, None
            all_results: list[types.Database | types.Page] = []
            while has_more and (limit is None or len(all_results) < limit):
                if start_cursor is not None:
                    args["params"]["start_cursor"] = start_cursor
                response = requests.post(**args)
                response.raise_for_status()
                response_json = response.json()
                has_more = response_json["has_more"]
                start_cursor = response_json["next_cursor"]
                all_results += TypeAdapter(list[types.Database | types.Page]).validate_python(
                    response_json["results"]
                )
            return all_results
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class SearchAsync(SearchBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None

    async def search_by_title(
        self,
        query: str | None = None,
        sort_obj: SearchBase._Sort | None = None,
        filter_obj: SearchBase._Filter | None = None,
        limit: int | None = None,
    ) -> list[types.Database | types.Page]:
        """Search for pages by title."""
        args = self._search_by_title_args(query, sort_obj, filter_obj)

        try:
            all_results: list[types.Database | types.Page] = []
            has_more, start_cursor = True, None

            while has_more and (limit is None or len(all_results) < limit):
                if start_cursor:
                    args["params"]["start_cursor"] = start_cursor
                assert self._session is not None
                async with self._session.post(**args, timeout=ASYNC_TIMEOUT) as response:
                    response.raise_for_status()
                    response_json = await response.json()

                    has_more = response_json.get("has_more", False)
                    start_cursor = response_json.get("next_cursor")
                    all_results += TypeAdapter(
                        list[types.Database | types.Page]
                    ).validate_python(response_json["results"])

            return all_results
        except aiohttp.ClientResponseError as e:
            raise _error_handler(e)


class UsersBase:
    def __init__(self, notion_api_key: str) -> None:
        self._token: str = notion_api_key

    def _retrieve_a_user_args(self, user_id: str) -> RequestBody:
        return RequestBody(
            url=f"https://api.notion.com/v1/users/{_format_block_id(user_id)}",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
        )

    def _list_all_users_args(self) -> RequestBodyWithParams:
        return RequestBodyWithParams(
            url="https://api.notion.com/v1/users",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
            params={"page_size": MAX_PAGE_SIZE},
        )

    def _retrieve_token_bot_user_args(self) -> RequestBody:
        return RequestBody(
            url="https://api.notion.com/v1/users/me",
            headers={
                "Authorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
            },
        )


class UsersSync(UsersBase):
    """Class to handle users in Notion."""

    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)

    def retrieve_a_user(self, user_id: str) -> types.User:
        """Retrieve a user by their ID."""
        args = self._retrieve_a_user_args(user_id)

        try:
            response = requests.get(**args, timeout=SYNC_TIMEOUT)
            response.raise_for_status()
            response_result = response.json()
            result = TypeAdapter(types.User).validate_python(response_result)
            return result
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"❌ Error retrieving user: {e}.") from e

    def list_all_users(self) -> list[types.User]:
        """List all users."""
        args = self._list_all_users_args()

        try:
            has_more, start_cursor = True, None
            all_results: list[types.User] = []
            while has_more:
                if start_cursor:
                    args["params"]["start_cursor"] = start_cursor

                response = requests.get(**args, timeout=SYNC_TIMEOUT)
                response.raise_for_status()
                response_json = response.json()

                has_more = response_json.get("has_more", False)
                start_cursor = response_json.get("next_cursor")

                all_results += TypeAdapter(list[types.User]).validate_python(
                    response_json.get("results", [])
                )
            return all_results
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)

    def retrieve_token_bot_user(self) -> types.BotUser:
        """Retrieve the token bot user."""
        args = self._retrieve_token_bot_user_args()

        try:
            response = requests.get(**args, timeout=SYNC_TIMEOUT)
            response.raise_for_status()
            response_result = response.json()
            result = TypeAdapter(types.BotUser).validate_python(response_result)
            return result
        except requests.exceptions.RequestException as e:
            raise _error_handler(e)


class UsersAsync(UsersBase):
    def __init__(self, notion_api_key: str) -> None:
        super().__init__(notion_api_key)
        self._session: aiohttp.ClientSession | None = None

    async def retrieve_a_user(self, user_id: str) -> types.User:
        """Retrieve a user by their ID."""
        args = self._retrieve_a_user_args(user_id)

        try:
            assert self._session is not None
            async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                response.raise_for_status()
                response_result = await response.json()
                return TypeAdapter(types.User).validate_python(response_result)
        except aiohttp.ClientResponseError as e:
            raise _error_handler(e)

    async def list_all_users(self) -> list[types.User]:
        """List all users."""
        args = self._list_all_users_args()

        try:
            assert self._session is not None
            has_more, start_cursor = True, None
            all_results: list[types.User] = []

            while has_more:
                if start_cursor:
                    args["params"]["start_cursor"] = start_cursor

                async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                    response.raise_for_status()
                    response_json = await response.json()

                    has_more = response_json.get("has_more", False)
                    start_cursor = response_json.get("next_cursor")

                    all_results += TypeAdapter(list[types.User]).validate_python(
                        response_json.get("results", [])
                    )
            return all_results
        except aiohttp.ClientResponseError as e:
            raise _error_handler(e)

    async def retrieve_token_bot_user(self) -> types.BotUser:
        """Retrieve the token bot user."""
        args = self._retrieve_token_bot_user_args()

        try:
            assert self._session is not None
            async with self._session.get(**args, timeout=ASYNC_TIMEOUT) as response:
                response.raise_for_status()
                response_result = await response.json()
                return TypeAdapter(types.BotUser).validate_python(response_result)
        except aiohttp.ClientResponseError as e:
            raise _error_handler(e)


class ClientBase:
    def __init__(self, notion_api_key: str | None = None) -> None:
        if notion_api_key is None:
            api_key_env = environ.get("NOTION_API_KEY")
            if api_key_env is None:
                raise ValueError(
                    "❌ NOTION_API_KEY not found in environment variables or passed as an "
                    + "argument. Please set it in your environment or pass it as an argument."
                )
            self._token = api_key_env
        else:
            self._token: str = notion_api_key


class Client(ClientBase):
    def __init__(self, notion_api_key: str | None = None) -> None:
        super().__init__(notion_api_key)

        self._auth = Auth(self._token)
        self._blocks = BlocksSync(self._token)
        self._pages = PagesSync(self._token)
        self._databases = DatabasesSync(self._token)
        self._comments = CommentsSync(self._token)
        self._file_uploads = FileUploadsSync(self._token)
        self._search = SearchSync(self._token)
        self._users = UsersSync(self._token)

    @property
    def auth(self) -> Auth:
        """Return the Auth object."""
        return self._auth

    @property
    def blocks(self) -> BlocksSync:
        """Return the Blocks object."""
        return self._blocks

    @property
    def pages(self) -> PagesSync:
        """Return the Pages object."""
        return self._pages

    @property
    def databases(self) -> DatabasesSync:
        """Return the Databases object."""
        return self._databases

    @property
    def comments(self) -> CommentsSync:
        """Return the Comments object."""
        return self._comments

    @property
    def file_uploads(self) -> FileUploadsSync:
        """Return the FileUploads object."""
        return self._file_uploads

    @property
    def search(self) -> SearchSync:
        """Return the Search object."""
        return self._search

    @property
    def user(self) -> UsersSync:
        """Return the Users object."""
        return self._users


class AsyncClient(ClientBase):
    def __init__(self, notion_api_key: str | None = None) -> None:
        super().__init__(notion_api_key)

        self._auth = AuthAsync(self._token)
        self._blocks = BlocksAsync(self._token)
        self._pages = PagesAsync(self._token)
        self._databases = DatabasesAsync(self._token)
        self._comments = CommentsAsync(self._token)
        self._file_uploads = FileUploadsAsync(self._token)
        self._search = SearchAsync(self._token)
        self._users = UsersAsync(self._token)

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=SYNC_TIMEOUT),
            headers={
                "AuthAsyncorization": f"Bearer {self._token}",
                "Notion-Version": NOTION_VERSION,
                "Content-Type": "application/json",
            },
        )

        # Pass session to all sub-clients
        self._auth._session = self._session
        self._blocks._session = self._session
        self.pages._session = self._session
        self.databases._session = self._session
        self.comments._session = self._session
        self.file_uploads._session = self._session
        self.search._session = self._session
        self.user._session = self._session

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    @property
    def auth(self) -> AuthAsync:
        """Return the AuthAsync object."""
        return self._auth

    @property
    def blocks(self) -> BlocksAsync:
        """Return the Blocks object."""
        return self._blocks

    @property
    def pages(self) -> PagesAsync:
        """Return the Pages object."""
        return self._pages

    @property
    def databases(self) -> DatabasesAsync:
        """Return the Databases object."""
        return self._databases

    @property
    def comments(self) -> CommentsAsync:
        """Return the Comments object."""
        return self._comments

    @property
    def file_uploads(self) -> FileUploadsAsync:
        """Return the FileUploads object."""
        return self._file_uploads

    @property
    def search(self) -> SearchAsync:
        """Return the Search object."""
        return self._search

    @property
    def user(self) -> UsersAsync:
        """Return the Users object."""
        return self._users
