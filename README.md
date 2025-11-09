# openfda-python

A comprehensive Python wrapper for the [openFDA API](https://open.fda.gov/) that provides easy access to FDA data on drugs, devices, foods, and other products.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features

- **Comprehensive API Coverage**: Support for all major openFDA endpoints including:
  - Drug NDC Directory
  - Drug Adverse Events
  - Drug Labels
  - Drug Enforcement Reports
  - Device Adverse Events
  - Device Classifications
  - Device Registrations and Listings
  - Food Adverse Events
  - And many more...

- **Smart Pagination**: Automatic handling of large result sets with hybrid pagination strategy
  - Skip/limit pagination for first 25,000 results
  - Automatic search_after pagination for results beyond 25,000
  - Support for unlimited result fetching

- **Rate Limiting**: Built-in rate limiter to respect FDA API limits
  - 240 requests per minute (default)
  - 1,000 requests per day (configurable)
  - Configurable limits for API key holders

- **Type-Safe Queries**: Strongly-typed query classes with validation
- **Pythonic API**: Clean, intuitive interface for building queries
- **Comprehensive Documentation**: Detailed docstrings and examples

## Installation

### Install directly from GitHub (Recommended)

You can install the package directly from GitHub without needing to publish to PyPI:

```bash
# Install the latest version from main branch
pip install git+https://github.com/dc-codes426/openfda-python.git

# Or install a specific version/tag
pip install git+https://github.com/dc-codes426/openfda-python.git@v0.1.0

# Or install in editable mode for development
git clone https://github.com/dc-codes426/openfda-python.git
cd openfda-python
pip install -e .
```

### Install from PyPI (if published)

```bash
pip install openfda-python
```

## Quick Start

```python
from api_client import FDAClient, Drug_NDCQuery

# Initialize the client
client = FDAClient()

# Create a query for Tylenol products
query = Drug_NDCQuery(
    search='brand_name:"tylenol"',
    limit=10
)

# Execute the search
results = client.api_search(query)

# Access results
print(f"Total results: {results.total_results}")
print(f"Retrieved: {len(results.records)} records")

# Access individual records
for record in results.records:
    data = record.raw_record
    print(f"Brand: {data.get('brand_name')}")
    print(f"Generic: {data.get('generic_name')}")
```

## Usage Examples

### Drug Adverse Events

```python
from api_client import FDAClient, DrugAdverseEventsQuery

client = FDAClient()

# Search for serious adverse events
query = DrugAdverseEventsQuery(
    search='serious:1 AND patient.drug.openfda.brand_name:"aspirin"',
    sort='receivedate:desc',
    limit=100
)

results = client.api_search(query)

for record in results.records:
    event = record.raw_record
    print(f"Report ID: {event.get('safetyreportid')}")
    print(f"Receive Date: {event.get('receivedate')}")
```

### Device Classifications

```python
from api_client import FDAClient, DeviceClassificationQuery

client = FDAClient()

# Search for Class II medical devices
query = DeviceClassificationQuery(
    search='device_class:2',
    limit=50
)

results = client.api_search(query)

for record in results.records:
    device = record.raw_record
    print(f"Device: {device.get('device_name')}")
    print(f"Class: {device.get('device_class')}")
```

### Large Result Sets (Unlimited Pagination)

```python
from api_client import FDAClient, Drug_NDCQuery

client = FDAClient()

# Fetch ALL available results (requires sort parameter for >25K results)
query = Drug_NDCQuery(
    search='finished:true',
    sort='brand_name:asc',
    limit=-1  # -1 means unlimited
)

# This will automatically paginate through all results
results = client.api_search(query)
print(f"Retrieved {len(results.records)} of {results.total_results} total records")
```

### Using API Key for Higher Rate Limits

```python
from api_client import FDAClient, RateLimiter

# Initialize with higher limits
client = FDAClient(
    max_requests_per_minute=240,
    max_requests_per_day=120000  # Much higher limit with API key
)

# Set your API key
client.set_api_key("your-api-key-here")

# Now you can make more requests per day
```

## Supported Endpoints

### Drug Endpoints
- `Drug_NDCQuery` - National Drug Code Directory
- `DrugAdverseEventsQuery` - Adverse event reports
- `DrugProductLabelingQuery` - Drug labeling information
- `DrugRecallEnforcementReportsQuery` - Drug recalls
- `DrugDrugsatFDAQuery` - Drugs@FDA data
- `DrugDrugShortagesQuery` - Drug shortage information

### Device Endpoints
- `DeviceAdverseEventsQuery` - Device adverse events
- `DeviceClassificationQuery` - Device classifications
- `DevicePremarketApprovalQuery` - PMA data
- `DeviceRegistrationsListingsQuery` - Device registrations
- `DeviceUniqueDeviceIDQuery` - UDI data
- `DeviceCovid19TestingEvalsQuery` - COVID-19 serology testing

### Other Endpoints
- `AnimalVetAdverseEventsQuery` - Animal/veterinary events
- `CosmeticEventsQuery` - Cosmetic adverse events
- `FoodAdverseEventsQuery` - Food adverse events
- `TobaccoProblemReportsQuery` - Tobacco problem reports
- `OtherSubstanceDataReportsQuery` - Substance data
- `OtherHistoricalDocumentsQuery` - Historical documents
- `TransparencyCRLSQuery` - Correspondence

## Query Parameters

All query classes support these common parameters:

- `search`: FDA API search query string (e.g., `'brand_name:"aspirin"'`)
- `sort`: Sort field and direction (e.g., `'receivedate:desc'`)
- `count`: Field to count unique values
- `limit`: Maximum records to retrieve (default: 1000, use -1 for unlimited)
- `skip`: Number of records to skip (for manual pagination)

## Rate Limiting

The client includes built-in rate limiting to respect FDA API limits:

- **Without API Key**: 240 requests/minute, 120,000/day
- **With API Key**: 240 requests/minute, unlimited/day

The rate limiter automatically manages request timing and will pause when limits are reached.

## Context Manager Support

```python
from api_client import FDAClient, Drug_NDCQuery

# Use as context manager for automatic cleanup
with FDAClient() as client:
    query = Drug_NDCQuery(search='brand_name:"tylenol"')
    results = client.api_search(query)
    print(f"Found {results.total_results} results")
# Session automatically closed
```

## Error Handling

```python
from api_client import FDAClient, Drug_NDCQuery
import requests

client = FDAClient()

try:
    query = Drug_NDCQuery(search='invalid_field:value')
    results = client.api_search(query)
except requests.exceptions.HTTPError as e:
    print(f"API error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=api_client --cov-report=html
```

### Code Formatting

```bash
# Format with black
black src/

# Lint with ruff
ruff check src/
```

## Requirements

- Python 3.8 or higher
- requests >= 2.25.0

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## API Key

Get a free API key from [openFDA](https://open.fda.gov/apis/authentication/) for higher rate limits.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This library is not officially associated with or endorsed by the FDA. It is an independent wrapper around the public openFDA API.

## Resources

- [openFDA API Documentation](https://open.fda.gov/apis/)
- [openFDA API Basics](https://open.fda.gov/apis/query-syntax/)
- [FDA API Fields Reference](https://open.fda.gov/apis/drug/ndc/)

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/dc-codes426/openfda-python).
