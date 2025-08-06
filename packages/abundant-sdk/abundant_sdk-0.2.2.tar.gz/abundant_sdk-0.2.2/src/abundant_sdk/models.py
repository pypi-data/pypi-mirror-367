"""Data models for the Abundant SDK."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, RootModel


class SupportedFeatures(BaseModel):
    """Features supported by an environment."""

    reset: bool
    state_tracking: bool
    api_access: bool


class Environment(BaseModel):
    """Environment information."""

    key: str
    name: str
    description: str
    category: str
    supported_features: SupportedFeatures


class Endpoints(BaseModel):
    """Endpoint URLs for an instance."""

    app_url: str
    api_url: str
    cdp_url: str
    debug_url: str | None = None


class TaskInfo(BaseModel):
    """Basic task information."""

    task_id: str
    name: str
    description: str


class TaskResponse(BaseModel):
    """Full task details for discovery."""

    task_id: str
    name: str
    description: str
    environment: str
    verifiers: list[dict[str, Any]]


class InstanceData(BaseModel):
    """Raw instance data from API."""

    instance_id: str
    status: str
    environment: dict[str, str]
    task: TaskInfo | None = None  # Optional - only if task bound
    endpoints: Endpoints
    control_url: str
    created_at: datetime
    expires_at: datetime | None = None


class BindTaskRequest(BaseModel):
    """Request to bind a task to an instance."""

    task_id: str


class BindTaskResponse(BaseModel):
    """Response from binding a task."""

    success: bool
    task: TaskInfo


class TaskDefinition(BaseModel):
    """Enhanced task definition with rich metadata."""

    task_id: str
    name: str
    description: str
    environment: str
    task_type: str  # "read" or "write"
    verifier_type: str  # "exact_match" or "soql"

    # Verification data
    reference_answer: str | None = None  # For exact_match
    soql_assertions: list[str] | None = None  # For soql

    # Rich metadata
    difficulty_level: str | None = None  # "low", "medium", "high"
    estimated_minutes: int | None = None
    reference_trajectory_steps: int | None = None
    initial_state: str | None = None
    initial_page: str | None = None

    # Versioning
    version: str = "1.0"
    created_at: str | None = None


class VerifyRequest(BaseModel):
    """Request for task verification."""

    task: TaskDefinition  # Required - complete task definition
    answer: str | None = None  # For read tasks - plain text answer


class VerifyResponse(BaseModel):
    """Response from verification endpoint."""

    success: bool
    function: str
    result: dict[str, Any]
    execution_time_ms: int





class CurrentPage(BaseModel):
    """Current page information."""

    url: str
    title: str


class LoggedInUser(BaseModel):
    """Logged in user information."""

    username: str
    profile: str


class Mutation(BaseModel):
    """Data mutation information."""

    timestamp: datetime
    type: str
    object: str
    record_id: str
    data: dict[str, Any]


class StateResponse(BaseModel):
    """Response from state endpoint."""

    current_page: CurrentPage
    logged_in_user: LoggedInUser
    recent_mutations: list[Mutation]


class CreateInstanceRequest(BaseModel):
    """Request to create a new instance."""

    environment: str  # Required - environment to create
    enable_browser_session: bool = True
    browser_provider: str = "browserbase"  # "browserbase" or "anchor"
