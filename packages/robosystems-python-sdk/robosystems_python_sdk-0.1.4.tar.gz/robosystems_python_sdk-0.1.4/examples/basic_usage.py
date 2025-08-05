"""Basic usage example for RoboSystems Python SDK."""

import asyncio
from robosystems_client import RoboSystemsClient
from robosystems_client.api.company.list_companies import (
  asyncio as list_companies_async,
  asyncio_detailed as list_companies_async_detailed,
)
from robosystems_client.api.status.get_service_status import (
  asyncio_detailed as get_service_status_async,
)

GRAPH_ID = "your-graph-id-here"
ROBOSYSTEMS_API_KEY = "your-api-key-here"


async def main():
  """Demonstrate basic SDK usage."""

  # Initialize the client with your API key
  client = RoboSystemsClient(
    base_url="https://api.robosystems.ai",  # or https://api.robosystems.ai for prod
    token=ROBOSYSTEMS_API_KEY,
    auth_header_name="X-API-Key",
    prefix="",  # No prefix needed for API key
  )

  print("🤖 RoboSystems Python SDK Example")
  print("=" * 40)

  try:
    # Check service status
    print("\n📊 Checking service status...")
    status_response = await get_service_status_async(client=client)
    print(f"Status: {status_response.status_code} - Service is healthy")

    # List companies in a specific graph (replace 'your-graph-id' with actual graph ID)
    print("\n🏢 Listing companies...")

    # Get detailed response to debug
    companies_response = await list_companies_async_detailed(
      graph_id=GRAPH_ID, client=client
    )
    print(f"Companies API Status: {companies_response.status_code}")
    print(f"Raw response: {companies_response.content[:200]}...")

    # Get parsed response
    companies = await list_companies_async(graph_id=GRAPH_ID, client=client)

    if companies:
      print(f"Found {len(companies.companies)} companies (total: {companies.total})")
      if companies.companies:
        for company in companies.companies[:3]:  # Show first 3
          print(f"  - {company.name} (ID: {company.identifier})")
    else:
      print("No companies response received")

  except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure your API key is valid and the service is running.")


if __name__ == "__main__":
  asyncio.run(main())
