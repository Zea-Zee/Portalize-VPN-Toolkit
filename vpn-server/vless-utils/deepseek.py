"""
Async client for 3x-ui panel API.
Documentation: https://www.postman.com/hsanaei/3x-ui/documentation/q1l5l0u/3x-ui
"""

import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

import aiohttp
from pydantic import BaseModel, Field


class APIError(Exception):
    """Base exception for all API-related errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)


class AuthError(APIError):
    """Authentication failed."""


class NotFoundError(APIError):
    """Resource not found."""


class ClientSettings(BaseModel):
    """Model for client settings."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    alterId: int = 0
    email: str
    limitIp: int = 0
    totalGB: int = 0
    expiryTime: int = 0
    enable: bool = True
    tgId: str = ""
    subId: str = ""


class TrafficStats(BaseModel):
    """Model for traffic statistics."""
    up: int
    down: int


class ClientTraffic(BaseModel):
    """Model for client traffic data."""
    email: str
    enable: bool
    expiryTime: int
    totalGB: int
    trafficStats: TrafficStats


class InboundType(str, Enum):
    """Supported inbound types."""
    VMESS = "vmess"
    VLESS = "vless"
    TROJAN = "trojan"
    SHADOWSOCKS = "shadowsocks"


class XUI:
    """
    Async client for 3x-ui panel API.

    Example usage:
    ```python
    async with XUI(base_url="http://example.com:2053", username="admin", password="admin") as xui:
        # List all inbounds
        inbounds = await xui.list_inbounds()

        # Add new client
        await xui.add_client(inbound_id=1, email="user@example.com")
    ```
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        verify_ssl: bool = False,
        timeout: int = 30,
    ):
        """
        Initialize the client.

        :param base_url: Base URL of the 3x-ui panel (e.g., "http://localhost:2053")
        :param username: Panel username
        :param password: Panel password
        :param verify_ssl: Verify SSL certificates
        :param timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session: Optional[aiohttp.ClientSession] = None
        self._cookies: Optional[Dict[str, str]] = None

    async def __aenter__(self):
        await self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _create_session(self):
        """Create a new aiohttp session."""
        self._session = aiohttp.ClientSession(
            base_url=self.base_url,
            timeout=self.timeout,
            cookie_jar=aiohttp.CookieJar(unsafe=True),
        )

    async def close(self):
        """Close the session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Tuple[Optional[Dict[str, Any]], Optional[APIError]]:
        """
        Make an authenticated request to the API.

        :param method: HTTP method (get, post, etc.)
        :param endpoint: API endpoint (e.g., "/panel/api/inbounds/list")
        :param kwargs: Additional arguments for aiohttp request
        :return: Tuple of (response_data, error)
        """
        if not self._session or self._session.closed:
            await self._create_session()

        try:
            async with self._session.request(
                method,
                endpoint,
                verify_ssl=self.verify_ssl,
                **kwargs
            ) as response:
                if response.status == 401:
                    return None, AuthError("Unauthorized", 401)

                try:
                    data = await response.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    text = await response.text()
                    return None, APIError(f"Invalid JSON response: {text}", response.status)

                if response.status >= 400:
                    error_msg = data.get(
                        "msg", data.get("error", "Unknown error"))
                    if response.status == 404:
                        return None, NotFoundError(error_msg, 404)
                    return None, APIError(error_msg, response.status)

                return data, None

        except asyncio.TimeoutError:
            return None, APIError("Request timeout")
        except aiohttp.ClientError as e:
            return None, APIError(f"Network error: {str(e)}")

    async def login(self) -> bool:
        """
        Authenticate with the panel.

        :return: True if login was successful
        :raises: AuthError if authentication fails
        """
        payload = {
            "username": self.username,
            "password": self.password
        }

        data, error = await self._request("POST", "/login", json=payload)
        if error:
            raise AuthError(f"Login failed: {error}")

        # Check if we have session cookie
        if not self._session or not self._session.cookie_jar:
            raise AuthError("No session cookie received")

        return True

    async def list_inbounds(self) -> List[Dict[str, Any]]:
        """
        List all inbounds.

        :return: List of inbounds
        :raises: APIError if request fails
        """
        data, error = await self._request("GET", "/panel/api/inbounds/list")
        if error:
            raise APIError(f"Failed to list inbounds: {error}:\n{data}")

        if not isinstance(data, list):
            raise APIError(f"Unexpected response format from list_inbounds:\n{data}")

        return data

    async def get_inbound(self, inbound_id: int) -> Dict[str, Any]:
        """
        Get details for a specific inbound.

        :param inbound_id: ID of the inbound to retrieve
        :return: Inbound details
        :raises: NotFoundError if inbound doesn't exist
        :raises: APIError if request fails
        """
        data, error = await self._request("GET", f"/panel/api/inbounds/get/{inbound_id}")
        if error:
            if isinstance(error, NotFoundError):
                raise NotFoundError(f"Inbound {inbound_id} not found")
            raise APIError(f"Failed to get inbound: {error}")

        return data

    async def add_client(
        self,
        inbound_id: int,
        client: ClientSettings,
        skip_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a new client to an inbound.

        :param inbound_id: ID of the inbound to add client to
        :param client: Client settings
        :param skip_existing: If True, skip if client already exists
        :return: API response
        :raises: APIError if request fails
        """
        if not isinstance(client, ClientSettings):
            client = ClientSettings(**client)

        payload = {
            "id": inbound_id,
            "settings": json.dumps({
                "clients": [client.dict()]
            })
        }

        data, error = await self._request("POST", "/panel/api/inbounds/addClient", json=payload)
        if error:
            if skip_existing and "already exists" in str(error):
                return {"status": "skipped", "message": "Client already exists"}
            raise APIError(f"Failed to add client: {error}")

        return data

    async def delete_client(self, inbound_id: int, email: str) -> bool:
        """
        Delete a client by email.

        :param inbound_id: ID of the inbound
        :param email: Client email to delete
        :return: True if deletion was successful
        :raises: NotFoundError if client doesn't exist
        :raises: APIError if request fails
        """
        payload = {
            "id": inbound_id,
            "email": email
        }

        _, error = await self._request("POST", "/panel/api/inbounds/delClient", json=payload)
        if error:
            if isinstance(error, NotFoundError):
                raise NotFoundError(f"Client {email} not found")
            raise APIError(f"Failed to delete client: {error}")

        return True

    async def update_client(
        self,
        inbound_id: int,
        client: ClientSettings
    ) -> Dict[str, Any]:
        """
        Update an existing client.

        :param inbound_id: ID of the inbound
        :param client: Updated client settings
        :return: API response
        :raises: NotFoundError if client doesn't exist
        :raises: APIError if request fails
        """
        if not isinstance(client, ClientSettings):
            client = ClientSettings(**client)

        payload = {
            "id": inbound_id,
            "settings": json.dumps({
                "clients": [client.dict()]
            })
        }

        data, error = await self._request("POST", "/panel/api/inbounds/updateClient", json=payload)
        if error:
            if isinstance(error, NotFoundError):
                raise NotFoundError(f"Client {client.email} not found")
            raise APIError(f"Failed to update client: {error}")

        return data

    async def get_client_traffic(self, email: str) -> ClientTraffic:
        """
        Get traffic statistics for a client.

        :param email: Client email
        :return: Client traffic data
        :raises: NotFoundError if client doesn't exist
        :raises: APIError if request fails
        """
        data, error = await self._request("GET", f"/panel/api/inbounds/getClientTraffic/{email}")
        if error:
            if isinstance(error, NotFoundError):
                raise NotFoundError(f"Client {email} not found")
            raise APIError(f"Failed to get client traffic: {error}")

        return ClientTraffic(**data)

    async def reset_client_traffic(self, email: str) -> bool:
        """
        Reset traffic statistics for a client.

        :param email: Client email
        :return: True if reset was successful
        :raises: NotFoundError if client doesn't exist
        :raises: APIError if request fails
        """
        _, error = await self._request("POST", f"/panel/api/inbounds/resetClientTraffic/{email}")
        if error:
            if isinstance(error, NotFoundError):
                raise NotFoundError(f"Client {email} not found")
            raise APIError(f"Failed to reset client traffic: {error}")

        return True


async def example_usage():
    """Example usage of the XUI client."""
    async with XUI(
        base_url='http://146.19.84.226:63421/',
        username='Kp9fI2bfj5',
        password='npYEcjPr5E',
        verify_ssl=False
    ) as xui:
        try:
            # List all inbounds
            inbounds = await xui.list_inbounds()
            print(f"Found {len(inbounds)} inbounds")

            if inbounds:
                # Get first inbound details
                inbound = await xui.get_inbound(inbounds[0]['id'])
                print(f"Inbound details: {inbound}")

                # Add new client
                client = ClientSettings(
                    email="test@example.com",
                    limitIp=2,
                    totalGB=100
                )
                result = await xui.add_client(inbounds[0]['id'], client)
                print(f"Added client: {result}")

                # Get client traffic
                traffic = await xui.get_client_traffic("test@example.com")
                print(f"Client traffic: {traffic}")

        except APIError as e:
            print(f"API error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(example_usage())
