"""Simple synchronous example for RoboSystems Python SDK."""

from robosystems_client import RoboSystemsClient
from robosystems_client.api.status.get_service_status import (
  sync_detailed as get_service_status_sync,
)
from robosystems_client.api.sec.list_sec_companies import (
  sync as list_sec_companies_sync,
)


def main():
  """Demonstrate basic synchronous SDK usage."""

  # Initialize the client with your API key
  client = RoboSystemsClient(
    base_url="http://localhost:8000",  # Use local dev server
    token="your-api-key-here",
    auth_header_name="X-API-Key",
    prefix="",  # No prefix needed for API key
  )

  print("🤖 RoboSystems Python SDK - Simple Example")
  print("=" * 45)

  try:
    # Check service status (synchronous)
    print("\n📊 Checking service status...")
    status_response = get_service_status_sync(client=client)
    print(f"Status: {status_response.status_code} - Service is healthy")

    # List SEC companies (synchronous)
    print("\n🏛️ Listing SEC companies...")
    sec_companies = list_sec_companies_sync(
      client=client,
      limit=3,  # Just get 3 for demo
    )

    if sec_companies and sec_companies.companies:
      print(f"Found {len(sec_companies.companies)} SEC companies:")
      for company in sec_companies.companies:
        print(f"  - {company.name} (CIK: {company.cik})")
    else:
      print("No companies found")

  except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure your API key is valid and the service is running.")


if __name__ == "__main__":
  main()
