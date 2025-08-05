# SDK Extensions

This directory contains extensions and enhancements to the auto-generated SDK that won't be overwritten when the SDK is regenerated from the OpenAPI specification.

## Why Extensions?

The main SDK is auto-generated from the OpenAPI spec using `openapi-python-client`. While this ensures the SDK stays in sync with API changes, it means any custom code added to the generated files will be lost on regeneration.

This extensions module provides a safe place for:
- Custom functionality that extends the base SDK
- Helper functions and utilities
- Enhanced implementations of API endpoints
- Streaming support and other advanced features

## Available Extensions

### Streaming Query Support

The `streaming` module provides NDJSON streaming support for large query results:

```python
from robosystems_client.extensions import asyncio_streaming, sync_streaming

# Process large datasets without loading everything into memory
async for chunk in asyncio_streaming(graph_id="sec", client=client, body=query):
    for row in chunk['data']:
        process_row(row)
```

## Adding New Extensions

When adding new extensions:

1. Create a new module in this directory
2. Add imports to `__init__.py`
3. Document the extension in this README
4. Update the main SDK README if it's a user-facing feature

Extensions should:
- Import from the parent package (`from .. import`) to use generated models and clients
- Follow the same naming conventions as the generated code
- Include comprehensive docstrings and type hints
- Handle errors gracefully