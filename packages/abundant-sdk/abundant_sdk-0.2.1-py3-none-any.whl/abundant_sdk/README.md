# Abundant Python SDK

Python SDK for the Abundant Environment API.

## Installation

```bash
pip install simulation-env-api[sdk]
```

## Quick Start

```python
import asyncio
from abundant_sdk import Client

async def main():
    async with Client(api_key="your-api-key") as client:
        # List environments
        envs = await client.list_environments()
        print(f"Available: {[e.key for e in envs]}")

        # List available tasks
        tasks = await client.list_tasks(environment="salesforce_sales")
        print(f"Available tasks: {[t.name for t in tasks]}")

        # Create instance with task binding
        instance = await client.create_instance(
            environment="salesforce_sales",
            task_id="1"  # Bind task at creation
        )
        print(f"CDP URL: {instance.cdp_url}")

        # Verify the bound task
        result = await instance.verify(answer="Negotiation/Review; 08-01-2025")
        print(f"Task success: {result.success}")

        # Get instance state
        state = await instance.get_state()
        print(f"Current page: {state.current_page.title}")

        # Execute SOQL queries
        query_result = await instance.execute_soql_query("SELECT Id, Name FROM Account LIMIT 5")
        print(f"Query results: {query_result}")

        # Clean up
        await instance.terminate()

asyncio.run(main())
```

## Features

- **Task System**: Bind tasks to instances and verify completion
- **Enhanced Instance Management**: List, filter, and manage instances
- **SOQL Integration**: Execute Salesforce Object Query Language queries
- **Data Export**: Export data from Salesforce objects
- **State Tracking**: Monitor current page, user, and data mutations
- **Async/await support**: Full async/await support with context managers
- **Type hints and Pydantic models**: Strong typing throughout
- **Browser Automation**: Integration with Playwright for browser automation

## API Reference

### Client Methods

- `list_environments()` - List available simulation environments
- `list_instances()` - List instances with optional filtering
- `list_tasks()` - List available tasks for environments
- `create_instance()` - Create new instance with optional task binding
- `get_instance()` - Get existing instance by ID

### Instance Methods

- `bind_task()` - Bind a task to the instance
- `verify()` - Verify the bound task with optional answer
- `get_state()` - Get current instance state
- `reset()` - Reset instance to clean state
- `execute_soql_query()` - Execute SOQL query
- `export_data()` - Export data from Salesforce objects
- `list_objects()` - List available Salesforce objects
- `terminate()` - Terminate the instance

## Examples

See the `examples/` directory for more detailed examples including RL training loops and task-based workflows.

## Version History

### v0.2.0
- Added comprehensive task system with binding and verification
- Enhanced instance management with filtering and listing
- Added SOQL query execution and data export capabilities
- Improved state tracking with detailed page and user information
- Updated all examples to use new task-based workflows
