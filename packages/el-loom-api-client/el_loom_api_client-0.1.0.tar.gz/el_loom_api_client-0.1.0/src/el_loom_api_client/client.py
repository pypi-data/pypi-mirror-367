import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from uuid import UUID

import requests

from .models import QECExperiment

LOOM_CONFIG_PATH = Path.home() / ".loom" / "config.json"

logger = logging.getLogger(__name__)


class LoomClient:
    def __init__(self, api_url: Optional[str] = None, api_token: Optional[str] = None):
        self.loom_api_url = api_url or self.__get_config_value(
            "api_url", "LOOM_API_URL"
        )
        self.loom_api_token = api_token or self.__get_config_value(
            "api_token", "LOOM_API_TOKEN"
        )

        if not self.loom_api_url or not self.loom_api_token:
            if not LOOM_CONFIG_PATH.exists():
                config_dir = LOOM_CONFIG_PATH.parent
                print(f"""
Error: Loom APIs configuration file not found!

Please create a config file at: {LOOM_CONFIG_PATH}
You may need to create the directory first: mkdir -p {config_dir}

The config file should contain JSON with the following structure:
{{
    "api_url": "https://your-loom-api-endpoint.com",
    "api_token": "your-api-token"
}}

Alternatively, you can set two environment variables:
- LOOM_API_URL
- LOOM_API_TOKEN
                """)
            raise ValueError("API URL and token must be set via env or config")

    ################################################################################################
    ## INTERNALS
    ################################################################################################

    def __get_config_value(self, key: str, env_var: str) -> Optional[str]:
        val = os.getenv(env_var)
        if val:
            return val
        if LOOM_CONFIG_PATH.is_file():
            with open(LOOM_CONFIG_PATH) as f:
                return json.load(f).get(key)

        return None

    def __get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.loom_api_token}",
            "Content-Type": "application/json",
        }

    def __get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        # Ensure the API URL is set
        if not self.loom_api_url:
            raise ValueError(
                "Loom API base URL is not set. Configure it in the config file or environment variable LOOM_API_URL."
            )

        url = self.loom_api_url.rstrip("/") + "/" + endpoint.lstrip("/")

        return requests.get(url, headers=self.__get_headers(), params=params)

    def __post(
        self, endpoint: str, data: Optional[Union[Dict[str, Any], str]] = None
    ) -> requests.Response:
        """
        Post data to the Loom API.

        Accepted data types:
            - Dict[str, Any]: Will be converted to a JSON payload
            - str: JSON string (will be sent as raw data with correct content type)

        Raises:
            ValueError: If the Loom API URL is not set.
        """

        # Ensure the API URL is set
        if not self.loom_api_url:
            raise ValueError(
                "Loom API base URL is not set. Configure it in the config file or environment variable LOOM_API_TOKEN."
            )

        url = self.loom_api_url.rstrip("/") + "/" + endpoint.lstrip("/")

        if isinstance(data, str):
            # If data is a JSON string, pass it directly as raw text, headers will set content type
            return requests.post(url, headers=self.__get_headers(), data=data)
        else:
            # If data is a dict or None, use json parameter from `requests`
            return requests.post(url, headers=self.__get_headers(), json=data)

    def __post_model(self, endpoint: str, model: Any) -> requests.Response:
        """
        Post a Pydantic model directly to the Loom API. The model will be dumped and transported as JSON.

        Args:
            endpoint: API endpoint to call
            model: Pydantic model instance (must have .model_dump() or .dict() method)

        Returns:
            requests.Response object
        """

        # Check if model has model_dump method (Pydantic v2+)
        if hasattr(model, "model_dump"):
            data = model.model_dump()
        # Fall back to .dict() for older Pydantic versions
        elif hasattr(model, "dict"):
            data = model.dict()
        else:
            raise TypeError(
                "Object must be a Pydantic model with .model_dump() or .dict() method"
            )

        return self.__post(endpoint, data)

    def __get_run_status(self, run_id: UUID) -> requests.Response:
        endpoint = f"/experiment_run/{run_id}"
        response = self.__get(endpoint)
        response.raise_for_status()

        return response

    def __get_run_result(self, run_id: UUID) -> requests.Response:
        endpoint = f"/experiment_run/{run_id}/result"
        response = self.__get(endpoint)
        response.raise_for_status()

        return response

    ################################################################################################
    ## PUBLIC METHODS
    ################################################################################################

    def experiment_run(self, experiment: QECExperiment) -> UUID:
        """
        Submit a memory experiment run to the Loom API.
        """

        response = self.__post_model("/experiment_run/", experiment)
        response.raise_for_status()
        result = response.json()
        return UUID(result.get("run_id"))

    def experiment_run_json(self, experiment: Dict[str, Any]) -> UUID:
        """
        Submit a memory experiment run to the Loom API.
        """

        response = self.__post("/experiment_run/", experiment)
        response.raise_for_status()
        result = response.json()
        return UUID(result.get("run_id"))

    def get_experiment_run_status(self, run_id: UUID) -> Dict[str, Any]:
        """
        Get the status of a specific experiment run by its ID.

        Args:
            run_id: UUID of the experiment run

        Returns:
            JSON object containing the run status
        """

        response = self.__get_run_status(run_id)

        return response.json()

    def get_experiment_run_result(self, run_id: UUID) -> Dict[str, Any]:
        """
        Get the result of a specific experiment run by its ID. Will return a 404 (not found) status
        error if no result is present for the given run ID.

        Use the `get_experiment_run_status` method first, to check the progress of the run.

        Args:
            run_id: UUID of the experiment run

        Returns:
            JSON object containing the run result or raises a 404 error if the result doesn't exist.
        """

        response = self.__get_run_result(run_id)

        return response.json()

    def get_result_sync(
        self, run_id: UUID, timeout: Optional[int] = None
    ) -> requests.Response:
        """
        Synchronously wait for and retrieve the result of an experiment run.
        This method blocks until the run is completed or fails.

        Args:
            run_id: UUID of the experiment run
            timeout: Optional timeout in seconds. If None, will wait indefinitely.

        Returns:
            JSON object containing the run result
        Raises:
            RuntimeError: If the experiment run fails or crashes
            TimeoutError: If the timeout is reached before the run completes
        """

        import time

        start_time = time.time()
        while True:
            status = self.__get_run_status(run_id).json()
            if status["state"] == "Completed" or status["state"] == "Cached":
                return self.__get_run_result(run_id).json()
            elif status["state"] == "Failed" or status["state"] == "Crashed":
                raise RuntimeError(f"Experiment run {run_id} failed: {status['state']}")

            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Timed out waiting for run {run_id} to complete")

            time.sleep(1)

    async def get_result_async(
        self, run_id: UUID, timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Asynchronously wait for and retrieve the result of an experiment run.

        This is the non-blocking version of get_result_sync.

        Args:
            run_id: UUID of the experiment run
            timeout: Optional timeout in seconds

        Returns:
            JSON object containing the run result

        Raises:
            RuntimeError: If the experiment run fails or crashes
            TimeoutError: If the timeout is reached before the run completes
        """

        import asyncio
        import time

        import httpx

        # Add this check to prevent None.rstrip() error
        if not self.loom_api_url:
            raise ValueError(
                "Loom API base URL is not set. Configure it in the config file or environment variable LOOM_API_URL."
            )

        start_time = time.time()

        # Create HTTP client for async requests
        async with httpx.AsyncClient() as client:
            while True:
                # Get status asynchronously
                status_url = f"{self.loom_api_url.rstrip('/')}/experiment_run/{run_id}"
                response = await client.get(status_url, headers=self.__get_headers())
                response.raise_for_status()
                status = response.json()

                if status["state"] == "Completed" or status["state"] == "Cached":
                    # Get result asynchronously
                    result_url = f"{self.loom_api_url.rstrip('/')}/experiment_run/{run_id}/result"
                    response = await client.get(
                        result_url, headers=self.__get_headers()
                    )
                    response.raise_for_status()
                    return response.json()
                elif status["state"] == "Failed" or status["state"] == "Crashed":
                    raise RuntimeError(
                        f"Experiment run {run_id} failed: {status['state']}"
                    )

                if timeout and (time.time() - start_time) > timeout:
                    raise TimeoutError(
                        f"Timed out waiting for run {run_id} to complete"
                    )

                # Non-blocking sleep
                await asyncio.sleep(1)
