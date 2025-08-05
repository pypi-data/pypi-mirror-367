"""Example of streaming query execution for large result sets."""

import asyncio
from robosystems_client import RoboSystemsClient
from robosystems_client.models.cypher_query_request import CypherQueryRequest
from robosystems_client.extensions import asyncio_streaming, sync_streaming


async def async_streaming_example():
  """Demonstrate asynchronous streaming query execution."""

  # Initialize the client
  client = RoboSystemsClient(
    base_url="https://api.robosystems.ai",
    token="your-api-key-here",
    auth_header_name="X-API-Key",
    prefix="",
  )

  # Prepare a query that returns a large dataset
  query_request = CypherQueryRequest(
    query="MATCH (c:Company) RETURN c.identifier, c.name, c.industry LIMIT 50000",
    parameters={"industry": "Technology"},
    timeout=30,
  )

  print("🚀 Starting async streaming query...")
  print("=" * 50)

  total_rows = 0
  chunk_count = 0

  try:
    # Execute streaming query
    async for chunk in asyncio_streaming(
      graph_id="sec",  # Or your graph ID
      client=client,
      body=query_request,
    ):
      chunk_count += 1
      rows_in_chunk = chunk.get("row_count", 0)
      total_rows += rows_in_chunk

      # Process the chunk data
      if chunk_count == 1:
        # First chunk includes column names
        print(f"📊 Columns: {chunk.get('columns', [])}")

      print(f"📦 Chunk {chunk_count}: {rows_in_chunk} rows")

      # Process each row in the chunk
      for row in chunk.get("data", []):
        # Your processing logic here
        # For demo, just show first row of each chunk
        if chunk.get("data", []).index(row) == 0:
          print(f"   Sample: {row}")

      # Check if this is the final chunk
      if chunk.get("final", False):
        execution_time = chunk.get("execution_time_ms", 0)
        print("\n✅ Query completed!")
        print(f"   Total rows: {total_rows}")
        print(f"   Total chunks: {chunk_count}")
        print(f"   Execution time: {execution_time}ms")

  except Exception as e:
    print(f"❌ Error during streaming: {e}")


def sync_streaming_example():
  """Demonstrate synchronous streaming query execution."""

  # Initialize the client
  client = RoboSystemsClient(
    base_url="http://localhost:8000",  # Local dev
    token="your-api-key-here",
    auth_header_name="X-API-Key",
    prefix="",
  )

  # Prepare a query
  query_request = CypherQueryRequest(
    query="MATCH (t:Transaction) WHERE t.amount > $min_amount RETURN t",
    parameters={"min_amount": 1000},
    timeout=30,
  )

  print("🚀 Starting sync streaming query...")
  print("=" * 50)

  total_rows = 0

  try:
    # Execute streaming query
    for chunk in sync_streaming(
      graph_id="company_123",
      client=client,
      body=query_request,
    ):
      rows_in_chunk = chunk.get("row_count", 0)
      total_rows += rows_in_chunk

      print(f"📦 Received chunk with {rows_in_chunk} rows")

      # Process chunk data
      for row in chunk.get("data", []):
        # Your processing logic here
        pass

    print(f"\n✅ Processed {total_rows} total rows")

  except Exception as e:
    print(f"❌ Error during streaming: {e}")


async def compare_streaming_vs_regular():
  """Compare streaming vs regular query execution."""

  client = RoboSystemsClient(
    base_url="https://api.robosystems.ai",
    token="your-api-key-here",
    auth_header_name="X-API-Key",
    prefix="",
  )

  query = "MATCH (c:Company)-[:HAS_FILING]->(f:Filing) RETURN c, f LIMIT 10000"

  print("📊 Comparing streaming vs regular query execution")
  print("=" * 50)

  # Regular query (loads all results into memory at once)
  from robosystems_client.api.query.execute_cypher_query import asyncio as execute_query

  print("\n1️⃣ Regular query (all results at once):")
  start_time = asyncio.get_event_loop().time()

  regular_result = await execute_query(
    graph_id="sec",
    client=client,
    body=CypherQueryRequest(query=query),
    streaming=False,  # Regular mode
  )

  regular_time = asyncio.get_event_loop().time() - start_time
  print(f"   ⏱️ Time: {regular_time:.2f}s")
  print(f"   💾 Rows in memory: {regular_result.row_count if regular_result else 0}")

  # Streaming query (processes results in chunks)
  print("\n2️⃣ Streaming query (chunked processing):")
  start_time = asyncio.get_event_loop().time()
  stream_rows = 0

  async for chunk in asyncio_streaming(
    graph_id="sec",
    client=client,
    body=CypherQueryRequest(query=query),
  ):
    stream_rows += chunk.get("row_count", 0)
    # Process chunk immediately, keeping memory usage low

  stream_time = asyncio.get_event_loop().time() - start_time
  print(f"   ⏱️ Time: {stream_time:.2f}s")
  print(f"   💾 Total rows processed: {stream_rows}")
  print("   📈 Memory efficient: Yes (chunked processing)")


if __name__ == "__main__":
  # Run async example
  print("🔄 Running async streaming example...\n")
  asyncio.run(async_streaming_example())

  print("\n" + "=" * 60 + "\n")

  # Run sync example
  print("🔄 Running sync streaming example...\n")
  sync_streaming_example()

  print("\n" + "=" * 60 + "\n")

  # Run comparison
  print("🔄 Running streaming vs regular comparison...\n")
  asyncio.run(compare_streaming_vs_regular())
