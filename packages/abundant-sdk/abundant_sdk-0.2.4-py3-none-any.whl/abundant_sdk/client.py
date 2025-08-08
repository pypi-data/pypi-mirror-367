"""Abundant Environment API client."""

import asyncio
from typing import Any

import httpx

from .models import (
    BindTaskRequest,
    BindTaskResponse,
    CreateInstanceRequest,
    Environment,
    InstanceData,
    StateResponse,
    TaskDefinition,
    TaskResponse,
    VerifyRequest,
    VerifyResponse,
)


class Instance:
    """Represents a running environment instance."""

    def __init__(self, client: "Client", data: InstanceData):
        self.client = client
        self.instance_id = data.instance_id
        self.environment = data.environment
        self.task = data.task
        self.endpoints = data.endpoints
        self.control_url = data.control_url
        self.status = data.status
        self.created_at = data.created_at
        self.expires_at = data.expires_at

    @property
    def app_url(self) -> str:
        """Salesforce Lightning UI URL."""
        return self.endpoints.app_url

    @property
    def api_url(self) -> str:
        """Salesforce REST API URL."""
        return self.endpoints.api_url

    @property
    def cdp_url(self) -> str:
        """Chrome DevTools Protocol URL for browser automation."""
        return self.endpoints.cdp_url

    @property
    def debug_url(self) -> str | None:
        """Browser debug URL if available."""
        return self.endpoints.debug_url

    async def bind_task(self, task_id: str) -> BindTaskResponse:
        """Bind a task to this instance."""
        request = BindTaskRequest(task_id=task_id)
        resp = await self.client._request(
            "POST",
            f"/v1/instances/{self.instance_id}/bind_task",
            json=request.model_dump(),
        )
        return BindTaskResponse(**resp)

    async def verify(self, task: TaskDefinition, answer: str | None = None) -> VerifyResponse:
        """Run verification for a task."""
        request = VerifyRequest(task=task, answer=answer)
        resp = await self.client._request(
            "POST",
            f"/v1/instances/{self.instance_id}/verify",
            json=request.model_dump(exclude_none=True),
        )
        return VerifyResponse(**resp)

    async def get_state(self) -> StateResponse:
        """Get current instance state."""
        resp = await self.client._request("GET", f"/v1/instances/{self.instance_id}/state")
        return StateResponse(**resp)

    async def terminate(self) -> None:
        """Terminate this instance."""
        await self.client._request("DELETE", f"/v1/instances/{self.instance_id}")


class Client:
    """Abundant Environment API client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.abundant.systems",
        timeout: float = 300.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = httpx.AsyncClient(headers={"x-api-key": api_key}, timeout=timeout)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Close the HTTP session."""
        await self.session.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Make an HTTP request."""
        url = f"{self.base_url}{path}"
        resp = await self.session.request(method, url, **kwargs)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError:
            # Try to get error details from response
            try:
                detail = resp.json()
                print(f"API Error Response: {detail}")
            except Exception:
                pass
            raise
        return resp.json()

    async def list_environments(self) -> list[Environment]:
        """List available environments."""
        data = await self._request("GET", "/v1/environments")
        return [Environment(**env) for env in data["environments"]]

    async def list_instances(
        self,
        status: str | None = None,
        environment: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Instance]:
        """List instances with optional filtering."""
        params = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        if environment:
            params["environment"] = environment

        data = await self._request("GET", "/v1/instances", params=params)
        return [Instance(self, InstanceData(**instance)) for instance in data]

    async def list_tasks(self, environment: str | None = None) -> list[TaskResponse]:
        """List available tasks."""
        params = {}
        if environment:
            params["environment"] = environment

        data = await self._request("GET", "/v1/tasks", params=params)
        return [TaskResponse(**task) for task in data["tasks"]]

    async def create_instance(
        self,
        environment: str,
        enable_browser_session: bool = True,
        browser_provider: str = "browserbase",
        poll_interval: float = 2.0,
        max_wait: float = 300.0,
    ) -> Instance:
        """Create a new environment instance and wait for it to be ready."""
        payload = CreateInstanceRequest(
            environment=environment,
            enable_browser_session=enable_browser_session,
            browser_provider=browser_provider,
        )

        data = await self._request("POST", "/v1/instances", json=payload.model_dump(exclude_none=True))
        instance_data = InstanceData(**data)

        # Poll until ready
        elapsed = 0.0
        while instance_data.status != "ready" and elapsed < max_wait:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            data = await self._request("GET", f"/v1/instances/{instance_data.instance_id}")
            instance_data = InstanceData(**data)

        if instance_data.status != "ready":
            raise TimeoutError(f"Instance {instance_data.instance_id} did not become ready within {max_wait} seconds")

        return Instance(self, instance_data)

    async def get_instance(self, instance_id: str) -> Instance:
        """Get an existing instance by ID."""
        data = await self._request("GET", f"/v1/instances/{instance_id}")
        return Instance(self, InstanceData(**data))


# Example usage
if __name__ == "__main__":

    async def main():
        async with Client(api_key="sk-...") as client:
            # List environments
            envs = await client.list_environments()
            print(f"Available: {[e.key for e in envs]}")

            # List tasks
            tasks = await client.list_tasks(environment="salesforce_sales")
            print(f"Available tasks: {[t.name for t in tasks]}")

            # Create instance
            instance = await client.create_instance(
                environment="salesforce_sales",
            )
            print("Instance ready!")
            print(f"CDP URL: {instance.cdp_url}")
            print(f"App URL: {instance.app_url}")

            # Verify task
            task = {
                "task_id": "1",
                "name": "Waterfront Property Portfolio Status",
                "description": "Find the Waterfront Property Portfolio opportunity and report its current stage and close date.",
                "environment": "salesforce_sales",
                "task_type": "read",
                "verifier_type": "exact_match",
                "reference_answer": "Negotiation/Review; 08-01-2025"
            }
            result = await instance.verify(task=task, answer="Negotiation/Review; 08-01-2025")
            print(f"Task success: {result.success}")

            # Get state
            state = await instance.get_state()
            print(f"Current page: {state.current_page.title}")

            # Terminate
            await instance.terminate()
            print("Instance terminated")

    asyncio.run(main())
