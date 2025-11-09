"""
FDA API client for fetching data from openFDA API.

This client works with any BaseQuery subclass (Drug_NDCQuery, DrugEventQuery, etc.)
using a single generic search() method.
"""
import logging
from typing import Dict, Any, Optional, List
import requests
import time
import threading
from .models import BaseQuery, Record, QueryResult

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API requests."""

    def __init__(self, max_requests: int, time_window: float):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds (e.g., 60 for per minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.last_update = time.time()
        self.lock = threading.Lock()

    def acquire(self):
        """
        Acquire a token for making a request.
        Blocks if rate limit is exceeded until a token becomes available.
        """
        with self.lock:
            now = time.time()
            # Refill tokens based on time elapsed
            elapsed = now - self.last_update
            self.tokens = min(
                self.max_requests,
                self.tokens + (elapsed * self.max_requests / self.time_window)
            )
            self.last_update = now

            # Wait if no tokens available
            if self.tokens < 1:
                sleep_time = (1 - self.tokens) * self.time_window / self.max_requests
                logger.info(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.tokens = 1
                self.last_update = time.time()

            # Consume a token
            self.tokens -= 1


class DailyQuotaLimiter:
    """Daily quota limiter that resets at midnight UTC."""

    def __init__(self, max_requests_per_day: int):
        """
        Initialize daily quota limiter.

        Args:
            max_requests_per_day: Maximum number of requests allowed per day
        """
        self.max_requests = max_requests_per_day
        self.requests_made = 0
        self.reset_time = self._calculate_next_midnight()
        self.lock = threading.Lock()

    def _calculate_next_midnight(self) -> float:
        """Calculate the timestamp for the next midnight UTC."""
        import datetime
        now = datetime.datetime.utcnow()
        # Next midnight is tomorrow at 00:00:00 UTC
        next_midnight = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
        return next_midnight.timestamp()

    def acquire(self):
        """
        Acquire permission for making a request.
        Blocks if daily quota is exhausted until midnight UTC.
        """
        with self.lock:
            now = time.time()

            # Reset counter if we've passed midnight
            if now >= self.reset_time:
                self.requests_made = 0
                self.reset_time = self._calculate_next_midnight()
                logger.info("Daily quota reset")

            # Check if quota is exhausted
            if self.requests_made >= self.max_requests:
                sleep_time = self.reset_time - now
                logger.info(f"Daily quota of {self.max_requests} requests exhausted. Sleeping until midnight UTC ({sleep_time:.0f} seconds)...")
                time.sleep(sleep_time)
                # After sleeping, reset
                self.requests_made = 0
                self.reset_time = self._calculate_next_midnight()

            # Increment counter
            self.requests_made += 1


class FDAClient:
    """Client for interacting with openFDA API (api.fda.gov)"""

    BASE_URL = "https://api.fda.gov"

    def __init__(self, timeout: int = 30, max_requests_per_minute: int = 240, max_requests_per_day: int = 1000):
        """
        Initialize the FDA API client.

        Args:
            timeout: Request timeout in seconds (default: 30)
            max_requests_per_minute: Maximum requests per minute (default: 240)
            max_requests_per_day: Maximum requests per day (default: 1000)

        Note:
            openFDA does not require an API key for basic usage.
            For higher rate limits, you can get a free API key from:
            https://open.fda.gov/apis/authentication/

            Default rate limits (without API key):
            - 240 requests per minute
            - 120,000 requests per day

            This client enforces conservative defaults (1000/day) but can be adjusted.
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FDAClient/1.0'
        })
        # Dual rate limiters: per-minute and per-day
        self.minute_limiter = RateLimiter(max_requests=max_requests_per_minute, time_window=60.0)
        self.day_limiter = DailyQuotaLimiter(max_requests_per_day=max_requests_per_day)

    def set_api_key(self, api_key: str) -> None:
        """
        Set API key for higher rate limits.

        Args:
            api_key: Your openFDA API key

        Note:
            Without an API key: 240 requests per minute, 120,000 per day
            With an API key: 240 requests per minute, no daily limit

            When setting an API key, you may want to adjust the daily limit:
            client.set_api_key(key)
            client.day_limiter = DailyQuotaLimiter(max_requests_per_day=120000)
        """
        self.session.params = {'api_key': api_key}

    def _build_params(self, query: BaseQuery, limit: Optional[int] = None, skip: Optional[int] = None) -> Dict[str, Any]:
        """
        Build API request parameters from a Pythonic query object.

        This method translates the user's Pythonic query into FDA API parameters.
        Handles FDA API-specific requirements:
        - Replaces spaces with '+' in search queries (FDA API requirement)

        Args:
            query: BaseQuery subclass with search parameters (not modified)
            limit: Optional override for limit parameter (used internally for pagination)
            skip: Optional override for skip parameter (used internally for pagination)

        Returns:
            Dict with API parameters ready for requests
        """
        params = {}

        # Translate Pythonic query fields to API parameters
        # FDA API requires spaces to be replaced with '+' in search queries
        if query.search:
            params['search'] = query.search.replace(' ', '+')
        if query.sort:
            params['sort'] = query.sort.replace(' ', '')
        if query.count:
            params['count'] = query.count.replace(' ', '+')

        # Use override values if provided (for pagination), otherwise use query values
        effective_limit = limit if limit is not None else query.limit
        effective_skip = skip if skip is not None else query.skip

        if effective_limit is not None and effective_limit != 1000:
            params['limit'] = effective_limit
        if effective_skip is not None and effective_skip > 0:
            params['skip'] = effective_skip

        return params

    def api_search(self, query: BaseQuery) -> QueryResult:
        """
        Generic search method with automatic hybrid pagination.

        This method handles all endpoint types and automatically paginates using
        a two-phase approach:

        Phase 1 (0-25,000 results): Uses skip/limit pagination (simple, efficient)
        Phase 2 (25,000+ results): Uses search_after pagination (requires sort parameter)

        Args:
            query: Any BaseQuery subclass with search parameters
                  - limit: Total number of records to retrieve
                           * Not specified: defaults to 1000
                           * Positive number: fetch that many results
                           * -1: fetch ALL available results (unlimited)
                  - sort: Required for retrieving more than 25,000 results
                          (e.g., "receivedate:asc")

        Returns:
            QueryResult object containing:
            - query: The original query object
            - total_results: Total number of matching records available
            - records: List of Record objects (up to limit)

        Raises:
            requests.exceptions.HTTPError: If API returns error status
            requests.exceptions.RequestException: For network errors

        Note:
            - For results beyond 25,000, a sort parameter is REQUIRED
            - Without sort, pagination stops at 25,000 results
            - The method seamlessly switches between pagination modes

        Example:
            ```python
            client = FDAClient()

            # Retrieve up to 1000 records (default)
            query = Drug_NDCQuery(search='brand_name:"tylenol"')
            results = client.api_search(query)

            # Retrieve up to 5000 records (automatic skip/limit pagination)
            query = DrugEventQuery(search='serious:1', limit=5000)
            results = client.api_search(query)

            # Retrieve more than 25,000 records (requires sort!)
            query = DrugEventQuery(
                search='serious:1',
                limit=50000,
                sort='receivedate:asc'  # Required for >25K results
            )
            results = client.api_search(query)

            # Retrieve ALL available results (unlimited mode)
            query = DrugEventQuery(
                search='serious:1',
                limit=-1,  # -1 means unlimited
                sort='receivedate:asc'  # Required for >25K results
            )
            result = client.api_search(query)
            print(f"Retrieved {len(result.records)} of {result.total_results} available results")
            ```
        """
        # Get user's requested parameters (query object remains unchanged)
        user_skip = query.skip or 0
        user_limit = query.limit or 1000

        # Handle unlimited results (limit=-1)
        unlimited_mode = (user_limit == -1)
        if unlimited_mode:
            user_limit = float('inf')  # Internal representation
            logger.info("Unlimited mode: will fetch all available results")

        # Initialize aggregation
        all_results = []
        current_skip = user_skip
        remaining = user_limit
        total_available = None  # Will be set from first API response

        # Get endpoint from query class attribute
        endpoint = f"{self.BASE_URL}{query.ENDPOINT_PATH}"

        try:
            # Phase 1: Use skip/limit for first 26,000 results
            while remaining > 0 and current_skip < 25000:
                # Calculate batch size (max 1000 per FDA API request)
                # Also respect total_available if known
                batch_size = min(remaining, 1000)
                if total_available is not None:
                    # Don't request more than what's left
                    remaining_in_dataset = total_available - (current_skip - user_skip)
                    batch_size = min(batch_size, remaining_in_dataset)
                    if batch_size <= 0:
                        logger.info("Reached end of available results based on total count")
                        break

                # Build API parameters from query with pagination overrides
                # Note: query object is NOT modified
                params = self._build_params(query, limit=batch_size, skip=current_skip)

                logger.info(f"Querying {endpoint} with params: {params} (skip/limit mode)")

                # Enforce rate limits before making request
                self.minute_limiter.acquire()
                self.day_limiter.acquire()

                # Make request
                response = self.session.get(endpoint, params=params, timeout=self.timeout)
                response.raise_for_status()

                data = response.json()
                raw_results = data.get('results', [])
                batch_results = [Record(raw_record=r) for r in raw_results]
                total_available = data.get('meta', {}).get('results', {}).get('total', 0)

                # Stop if no results returned
                if not batch_results:
                    logger.info("No more results available from API")
                    break

                # Add to aggregated results
                all_results.extend(batch_results)
                logger.info(f"Retrieved {len(all_results)} of {total_available} total available records")

                # Stop if we got fewer results than requested (end of dataset)
                if len(batch_results) < batch_size:
                    logger.info(f"Received partial batch ({len(batch_results)} < {batch_size}), no more results available")
                    break

                # Stop if we've now retrieved all available results
                if len(all_results) >= total_available:
                    logger.info(f"Retrieved all {total_available} available results")
                    break

                # Update for next iteration
                remaining -= len(batch_results)
                current_skip += len(batch_results)

            # Phase 2: Use search_after for results beyond 26,000
            if remaining > 0 and current_skip >= 25000 and len(all_results) < total_available:
                logger.info("Switching to search_after mode for results beyond 25,000")

                # search_after requires a sort parameter
                if not query.sort:
                    logger.warning("Cannot use search_after without a sort parameter. Stopping at 25,000 results.")
                else:
                    # Build initial search_after query (no skip parameter)
                    params = self._build_params(query, limit=min(remaining, 1000), skip=None)

                    while remaining > 0:
                        logger.info(f"Querying {endpoint} with params: {params} (search_after mode)")

                        # Enforce rate limits before making request
                        self.minute_limiter.acquire()
                        self.day_limiter.acquire()

                        response = self.session.get(endpoint, params=params, timeout=self.timeout)
                        response.raise_for_status()

                        data = response.json()
                        raw_results = data.get('results', [])
                        batch_results = [Record(raw_record=r) for r in raw_results]

                        if not batch_results:
                            logger.info("No more results available from search_after")
                            break

                        all_results.extend(batch_results)
                        remaining -= len(batch_results)
                        logger.info(f"Retrieved {len(all_results)} of {total_available} total available records")

                        # Check if we've retrieved all available results
                        if len(all_results) >= total_available:
                            logger.info(f"Retrieved all {total_available} available results")
                            break

                        # Extract next page URL from Link header
                        link_header = response.headers.get('Link', '')
                        if 'rel="next"' not in link_header:
                            logger.info("No more pages available (no Link header)")
                            break

                        # Parse the next URL from Link header
                        # Format: <URL>; rel="next"
                        import re
                        match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
                        if not match:
                            logger.warning("Could not parse Link header for next page")
                            break

                        next_url = match.group(1)
                        # Extract query parameters from next URL
                        from urllib.parse import urlparse, parse_qs
                        parsed = urlparse(next_url)
                        params = parse_qs(parsed.query)
                        # Convert to single values (parse_qs returns lists)
                        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}

            return QueryResult(
                query=query,
                total_results=total_available or 0,
                records=all_results
            )

        except requests.exceptions.HTTPError as e:
            # Try to extract error message from FDA API response
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', str(e))
                logger.error(f"FDA API error: {error_msg}")
            except:
                logger.error(f"FDA API HTTP error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error querying FDA API: {e}")
            raise

    def close(self):
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
