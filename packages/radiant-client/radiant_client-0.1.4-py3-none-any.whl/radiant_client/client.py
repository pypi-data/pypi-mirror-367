"""Async Python client for the Radiant Stears API.

This module wraps every public endpoint exposed by the Rust service shown
in the documentation:

*   `GET  /health`                                               – service liveness (no auth)
*   `GET  /v1/artifacts`                                         – list available artifacts
*   `POST /v1/artifacts/{artifact_name}/extract-transactions`.   – send URLs for extraction
*   `GET  /v1/calls/{call_id}`                                   – get call status and details

Usage example (see bottom of file):

```python
import asyncio

async def main():
    client = AsyncClient()
    print(await client.health_check())
    print(await client.get_artifacts())
    await client.close()

asyncio.run(main())
```
"""

from dataclasses import dataclass
import os
from typing import List, Optional, Union, Any, Dict
import asyncio
import time

import requests
import aiohttp
from dotenv import load_dotenv

__all__ = [
    "Client",
    "AsyncClient",
    "ClientError",
]


class ClientError(RuntimeError):
    """Base class for all client‑side errors."""


class Client:
    """Lightweight wrapper around the Radiant Stears project HTTP API.

    Parameters
    ----------
    api_key:
        The *Polaris* / *Radiant* API key. If ``None`` (default) the client
        looks for **API_KEY** in the environment (populate it via an
        ``.env`` file).
    base_url:
        The root of the Stears project server. *Do not* include a trailing
        slash.
    timeout:
        Seconds before aborting any single HTTP request.
    session:
        Optionally supply a pre‑configured ``requests.Session`` (useful for
        retries, custom adapters, etc.). If omitted the client creates its
        own ephemeral session on each call.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: int | float = 30,
        session: Optional[requests.Session] = None,
    ) -> None:
        load_dotenv(override=False)
        self.api_key: str | None = api_key or os.getenv("API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL")
        self.timeout = timeout
        self._session = session  # can be None → we fall back to requests

        if not self.api_key:
            raise ClientError(
                "API key not supplied and API_KEY not found in environment."
            )
            
        if not self.base_url:
            raise ClientError(
                "Base URL not supplied and BASE_URL not found in environment."
            )

    # ------------------------------------------------------------------ #
    # Public methods – one per endpoint ↓                                 #
    # ------------------------------------------------------------------ #
    def health_check(self) -> Dict[str, Any]:
        """Ping the service (no authentication required)."""
        return self._request("GET", "/health", auth=False).json()

    def get_artifacts(self) -> Dict[str, Any]:
        """Retrieve a list of available artifact names."""
        return self._request("GET", "/v1/artifacts").json()

    def extract_transactions(
        self,
        artifact_name: str,
        *,
        urls: List[str],
    ) -> Dict[str, Any]:
        """Trigger transaction extraction on the given *artifact*.

        Supply ``urls``.
        """
        self._validate_urls(urls)

        path = f"/v1/artifacts/{artifact_name}/extract-transactions"

        return self._request("POST", path, json=urls).json()

    def get_call(self, call_id: str) -> Dict[str, Any]:
        """Return the current status and details of a call."""
        path = f"/v1/calls/{call_id}"
        return self._request("GET", path).json()

    def wait_for_completion(
        self, 
        call_id: str, 
        *,
        poll_interval: float = 2.0,
        max_wait_time: float = 300.0
    ) -> Dict[str, Any]:
        """Poll a call until completion or timeout.
        
        Parameters
        ----------
        call_id:
            The call ID to monitor
        poll_interval:
            Seconds between status checks
        max_wait_time:
            Maximum time to wait before giving up
            
        Returns
        -------
        Dict containing the final call status and data
        
        Raises
        ------
        ClientError:
            If the call fails or times out
        """
        start_time = time.time()
        
        while True:
            call_status = self.get_call(call_id)
            status = call_status.get("status", "Unknown")
            
            print(f"Call {call_id} status: {status}")
            
            if status == "Completed":
                return call_status
            elif status == "Error":
                raise ClientError(f"Call {call_id} failed")
            elif time.time() - start_time > max_wait_time:
                raise ClientError(f"Call {call_id} timed out after {max_wait_time}s")
            
            time.sleep(poll_interval)

    # ------------------------------------------------------------------ #
    # Internal helpers ↓                                                 #
    # ------------------------------------------------------------------ #
    def _request(
        self,
        method: str,
        path: str,
        *,
        auth: bool = True,
        **kwargs: Any,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = kwargs.pop("headers", {})

        # Inject headers if the endpoint requires authentication.
        if auth:
            headers.setdefault("x-api-key", self.api_key)
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json")

        req_func = self._session.request if self._session else requests.request
        response = req_func(method, url, headers=headers, timeout=self.timeout, **kwargs)

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            message = (
                f"{method} {url} returned {response.status_code}: "
                f"{response.text.strip()}"
            )
            raise ClientError(message) from exc
        return response

    @staticmethod
    def _validate_urls(
        urls: List[str]
    ) -> None:
        if not isinstance(urls, list):
            raise TypeError("'urls' must be a list of strings.")
        if not urls:
            raise ValueError("'urls' list is empty.")
        if any(not (isinstance(u, str) and u.strip()) for u in urls):
            raise ValueError("'urls' contains empty or non‑string entries.")

class AsyncClient:
    """Async lightweight wrapper around the Radiant Stears project HTTP API.

    Parameters
    ----------
    api_key:
        The *Polaris* / *Radiant* API key. If ``None`` (default) the client
        looks for **API_KEY** in the environment (populate it via an
        ``.env`` file).
    base_url:
        The root of the Stears project server. *Do not* include a trailing
        slash.
    timeout:
        Seconds before aborting any single HTTP request.
    session:
        Optionally supply a pre‑configured ``aiohttp.ClientSession`` (useful for
        retries, custom connectors, etc.). If omitted the client creates its
        own session that should be closed with ``close()`` or used as an
        async context manager.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: Union[int, float] = 30,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        load_dotenv(override=False)
        self.api_key: str | None = api_key or os.getenv("API_KEY")
        self.base_url: str | None = base_url or os.getenv("BASE_URL")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._session = session
        self._own_session = session is None  # Track if we created the session

        if not self.api_key:
            raise ClientError(
                "API key not supplied and API_KEY not found in environment."
            )
        
        if not self.base_url:
            raise ClientError(
                "Base URL not supplied and BASE_URL not found in environment."
            )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the underlying aiohttp session if we created it."""
        if self._own_session and self._session:
            await self._session.close()
            self._session = None

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    # ------------------------------------------------------------------ #
    # Public methods – one per endpoint ↓                                 #
    # ------------------------------------------------------------------ #
    async def health_check(self) -> Dict[str, Any]:
        """Ping the service (no authentication required)."""
        return await self._request("GET", "/health", auth=False)

    async def get_artifacts(self) -> Dict[str, Any]:
        """Retrieve a list of available artifact names."""
        return await self._request("GET", "/v1/artifacts")

    async def extract_transactions(
        self,
        artifact_name: str,
        *,
        urls: List[str],
    ) -> Dict[str, Any]:
        """Trigger transaction extraction on the given *artifact*.

        Supply ``urls``.
        """
        self._validate_urls(urls)

        path = f"/v1/artifacts/{artifact_name}/extract-transactions"

        return await self._request("POST", path, json=urls)

    async def get_call(self, call_id: str) -> Dict[str, Any]:
        """Return the current status and details of a call."""
        path = f"/v1/calls/{call_id}"
        return await self._request("GET", path)

    async def wait_for_completion(
        self, 
        call_id: str, 
        *,
        poll_interval: float = 2.0,
        max_wait_time: float = 300.0
    ) -> Dict[str, Any]:
        """Async poll a call until completion or timeout.
        
        Parameters
        ----------
        call_id:
            The call ID to monitor
        poll_interval:
            Seconds between status checks
        max_wait_time:
            Maximum time to wait before giving up
            
        Returns
        -------
        Dict containing the final call status and data
        
        Raises
        ------
        ClientError:
            If the call fails or times out
        """
        start_time = time.time()
        
        while True:
            call_status = await self.get_call(call_id)
            status = call_status.get("status", "Unknown")
            
            print(f"Call {call_id} status: {status}")
            
            if status == "Completed":
                return call_status
            elif status == "Failed":
                raise ClientError(f"Call {call_id} failed")
            elif time.time() - start_time > max_wait_time:
                raise ClientError(f"Call {call_id} timed out after {max_wait_time}s")
            
            await asyncio.sleep(poll_interval)

    # ------------------------------------------------------------------ #
    # Internal helpers ↓                                                 #
    # ------------------------------------------------------------------ #
    async def _request(
        self,
        method: str,
        path: str,
        *,
        auth: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = kwargs.pop("headers", {})

        # Inject headers if the endpoint requires authentication.
        if auth:
            headers.setdefault("x-api-key", self.api_key)
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json")

        session = self._get_session()
        
        try:
            async with session.request(method, url, headers=headers, **kwargs) as response:
                # Check for HTTP errors
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as exc:
            # Handle aiohttp-specific errors
            message = f"{method} {url} failed: {exc}"
            raise ClientError(message) from exc
        except Exception as exc:
            # Handle other errors (like HTTP status errors)
            if hasattr(exc, 'status'):
                try:
                    error_text = await response.text()
                except:
                    error_text = str(exc)
                message = (
                    f"{method} {url} returned {exc.status}: "
                    f"{error_text.strip()}"
                )
            else:
                message = f"{method} {url} failed: {exc}"
            raise ClientError(message) from exc

    @staticmethod
    def _validate_urls(
        urls: List[str],
    ) -> None:
        if not isinstance(urls, list):
            raise TypeError("'urls' must be a list of strings.")
        if not urls:
            raise ValueError("'urls' list is empty.")
        if any(not (isinstance(u, str) and u.strip()) for u in urls):
            raise ValueError("'urls' contains empty or non‑string entries.")


# ---------------------------------------------------------------------- #
# Simple demonstration (will execute when `python client.py` is run)
# ---------------------------------------------------------------------- #
if __name__ == "__main__":
    import asyncio
    import json
    import sys

    async def main():
        urls = [
            # Put your URLs here to test extraction
            # "https://example.com/statement1",
            # "https://example.com/statement2",
        ]
        
        try:
            # Using as context manager (recommended)
            async with AsyncClient(base_url="http://localhost:3000", api_key="password") as client:
                print("→ Health check:")
                health = await client.health_check()
                print(json.dumps(health, indent=2))

                print("\n→ Artifacts:")
                artifacts = await client.get_artifacts()
                print(json.dumps(artifacts, indent=2))

                if artifacts.get("artifacts"):
                    default_artifact = artifacts["artifacts"][0]
                    try:
                        print(f"\n→ Extracting transactions with artifact '{default_artifact}':")
                        print(f"URLs: {urls}")
                        
                        # Step 1: Start extraction
                        extraction_response = await client.extract_transactions(
                            artifact_name=default_artifact,
                            urls=urls,
                        )
                        print(f"Extraction started: {json.dumps(extraction_response, indent=2)}")
                        
                        # Step 2: Get call ID from response
                        call_id = extraction_response.get("action_call")
                        if not call_id:
                            print("Error: No call ID returned from extraction")
                            return
                        
                        print(f"\n→ Polling call {call_id} for completion...")
                        
                        # Step 3: Wait for completion
                        final_result = await client.wait_for_completion(call_id)
                        
                        # Step 4: Display results
                        print(f"\n→ Final result:")
                        print(json.dumps(final_result, indent=2))
                        
                        # Step 5: Print successful extractions
                        data = final_result.get("result", {})
                        content = data.get("content", {})
                        successful = content.get("successful", [])
                        
                        if successful:
                            print(f"\n→ Successfully processed {len(successful)} URL(s):")
                            for i, result in enumerate(successful, 1):
                                print(f"\n--- Result {i} ---")
                                print(f"URL: {result.get('url', 'Unknown')}")
                                print(f"Scraped at: {result.get('scraped_at', 'Unknown')}")
                                
                                entities = result.get("entities", [])
                                if entities:
                                    print(f"Found {len(entities)} transaction(s):")
                                    for j, entity in enumerate(entities, 1):
                                        print(f"\n  Transaction {j}:")
                                        for key, value in entity.items():
                                            print(f"    {key}: {value}")
                                else:
                                    print("    No entities found")
                        else:
                            print("\n→ No successful extractions found")
                        
                        # Print failed URLs if any
                        failed = content.get("failed", [])
                        if failed:
                            print(f"\n→ Failed to process {len(failed)} URL(s):")
                            for failure in failed:
                                print(f"  - {failure}")

                    except ClientError as err:
                        print(f"Extraction failed: {err}")

                print("\nDemo complete.")

        except ClientError as err:
            sys.exit(f"Cannot run demo – {err}")

    # Alternative usage pattern without context manager
    async def alternative_usage():
        client = AsyncClient(base_url="http://localhost:3000", api_key="test")
        try:
            health = await client.health_check()
            print(json.dumps(health, indent=2))
        finally:
            await client.close()  # Important: close the session

    asyncio.run(main())
