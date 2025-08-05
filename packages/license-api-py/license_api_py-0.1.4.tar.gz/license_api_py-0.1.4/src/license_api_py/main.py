import httpx
from pydantic import BaseModel
import asyncio


class LoginRequest(BaseModel):
    key: str
    hwid: str


class LicenseAPI:
    def __init__(self, url):
        """
        Initialize the LicenseAPI with the given URL.

        Args:
            url (str): The base URL of the license API.
        """
        self.url: str = url

    async def login(self, creds: LoginRequest) -> bool:
        """
        Login to the license API

        Args:
            creds (LoginRequest): The login credentials.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.url}/license/auth",
                json=creds
            )

            response.raise_for_status()

        return True