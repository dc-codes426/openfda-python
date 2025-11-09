""""
Simple script, used mostly for testing.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import FDAClient, Drug_NDCQuery
from src.api_client.models import QueryResult, Record

client = FDAClient()

search_string = 'finished:true'

query = Drug_NDCQuery(search=search_string)

response = client.api_search(query)

print(f"Total results: {response.total_results}")
print(f"Records retrieved: {len(response.records)}")
if response.records:
    print(f"First record: {response.records[0].raw_record}")

