# RoboSystems Python SDK

Python SDK for the RoboSystems financial graph database API. This SDK provides easy access to RoboSystems' comprehensive financial data platform including accounting data, SEC filings, and graph-based analytics.

## Features

- **Type-safe API client** with full type hints and Pydantic models
- **Async/await support** for high-performance applications  
- **Multi-tenant support** with graph-scoped operations
- **Authentication handling** with API key management
- **Comprehensive error handling** with custom exceptions
- **Pagination support** for large data sets
- **Streaming query support** for memory-efficient processing of large result sets

## Installation

```bash
pip install robosystems-python-sdk
```

## Quick Start

```python
from robosystems_client import RoboSystemsClient
from robosystems_client.api.company.list_companies import sync as list_companies_sync, asyncio as list_companies_async
from robosystems_client.api.sec.list_sec_companies import sync as list_sec_companies_sync, asyncio as list_sec_companies_async

# Initialize the client
client = RoboSystemsClient(
    base_url="https://api.robosystems.ai",
    token="your-api-key",
    auth_header_name="X-API-Key",
    prefix=""  # No prefix needed for API key
)

# Synchronous usage
companies = list_companies_sync(graph_id="your-graph-id", client=client)
sec_companies = list_sec_companies_sync(client=client, limit=10)

# Async usage
import asyncio

async def main():
    companies = await list_companies_async(graph_id="your-graph-id", client=client)
    sec_companies = await list_sec_companies_async(client=client, limit=10)

asyncio.run(main())
```

### Function Patterns

The SDK provides multiple ways to call each API endpoint:

- **`sync()`** - Synchronous call, returns parsed response
- **`sync_detailed()`** - Synchronous call, returns full Response object  
- **`asyncio()`** - Asynchronous call, returns parsed response
- **`asyncio_detailed()`** - Asynchronous call, returns full Response object

## Streaming Queries

For large result sets, the SDK supports streaming responses that process data in chunks to minimize memory usage:

```python
from robosystems_client.extensions import asyncio_streaming
from robosystems_client.models.cypher_query_request import CypherQueryRequest

# Async streaming
async def process_large_dataset():
    query = CypherQueryRequest(
        query="MATCH (c:Company) RETURN c LIMIT 100000",
        parameters={"industry": "Technology"}
    )
    
    async for chunk in asyncio_streaming(
        graph_id="sec",
        client=client,
        body=query
    ):
        # Process chunk with chunk['row_count'] rows
        for row in chunk['data']:
            process_row(row)
        
        # Final chunk includes execution_time_ms
        if chunk.get('final'):
            print(f"Query completed in {chunk['execution_time_ms']}ms")

# Sync streaming also available
from robosystems_client.extensions import sync_streaming

for chunk in sync_streaming(graph_id="sec", client=client, body=query):
    # Process chunk
    pass
```

Streaming is ideal for:
- Exporting large datasets without loading everything into memory
- Real-time processing of query results
- Building data pipelines with controlled memory usage

## Development

This SDK is auto-generated from the RoboSystems OpenAPI specification to ensure it stays in sync with the latest API changes.

### Setup

```bash
just venv
just install
```

### Regenerating the SDK

When the API changes, regenerate the SDK from the OpenAPI spec:

```bash
# From localhost (development)
just generate-sdk http://localhost:8000/openapi.json

# From staging
just generate-sdk https://staging.api.robosystems.ai/openapi.json

# From production
just generate-sdk https://api.robosystems.ai/openapi.json
```

### Testing

```bash
just test
just test-cov
```

### Code Quality

```bash
just lint
just format
just typecheck
```

### Publishing

```bash
just build-package
just publish-package
```
