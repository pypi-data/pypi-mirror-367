"""
Custom exceptions for the Uber Central API client.

These exceptions provide specific error handling for different API failure scenarios.
"""


class UberCentralError(Exception):
    """
    Base exception for all Uber Central API errors.
    
    This is the parent class for all client-specific exceptions.
    Catch this to handle any API-related error.
    """
    pass


class AuthenticationError(UberCentralError):
    """
    Raised when API key authentication fails.
    
    This typically indicates:
    - Invalid API key
    - Expired API key
    - Missing Authorization header
    
    Example:
        ```python
        try:
            client = UberCentralClient(api_key="invalid-key")
        except AuthenticationError as e:
            print(f"Authentication failed: {e}")
        ```
    """
    pass


class ClientNotFoundError(UberCentralError):
    """
    Raised when a client_id is not found or invalid.
    
    This typically indicates:
    - Using a non-existent client_id
    - Client account was deactivated
    - Typo in client_id parameter
    
    Example:
        ```python
        try:
            estimates = client.get_estimates(
                client_id="invalid-client-id",
                pickup_address="123 Main St",
                dropoff_address="456 Oak Ave"
            )
        except ClientNotFoundError as e:
            print(f"Client not found: {e}")
            # Call initialize_user() to create account
        ```
    """
    pass


class RideNotFoundError(UberCentralError):
    """
    Raised when a ride_id is not found or invalid.
    
    This typically indicates:
    - Using a non-existent ride_id
    - Ride was already cancelled or completed
    - Typo in ride_id parameter
    
    Example:
        ```python
        try:
            status = client.get_ride_status("invalid-ride-id")
        except RideNotFoundError as e:
            print(f"Ride not found: {e}")
        ```
    """
    pass


class ValidationError(UberCentralError):
    """
    Raised when request parameters fail validation.
    
    This typically indicates:
    - Invalid phone number format
    - Invalid pickup time (past date, too far future)
    - Missing required fields
    - Invalid address format
    
    Example:
        ```python
        try:
            ride = client.book_ride(
                client_id="valid-client-id",
                pickup_address="",  # Empty address
                dropoff_address="123 Main St",
                rider_name="John Doe",
                rider_phone="invalid-phone"
            )
        except ValidationError as e:
            print(f"Validation failed: {e}")
        ```
    """
    pass


class BookingError(UberCentralError):
    """
    Raised when ride booking or scheduling fails.
    
    This typically indicates:
    - No drivers available in area
    - Uber service unavailable
    - Invalid pickup/dropoff locations
    - Scheduling conflicts
    - Account or payment issues
    
    Example:
        ```python
        try:
            ride = client.book_ride(
                client_id="valid-client-id",
                pickup_address="Middle of ocean",  # Invalid location
                dropoff_address="123 Main St",
                rider_name="John Doe", 
                rider_phone="9167995790"
            )
        except BookingError as e:
            print(f"Booking failed: {e}")
        ```
    """
    pass


class RateLimitError(UberCentralError):
    """
    Raised when API rate limits are exceeded.
    
    This typically indicates:
    - Too many requests per hour (1000+ requests)
    - Too many concurrent bookings (10+ simultaneous)
    - Temporary throttling due to high load
    
    Example:
        ```python
        try:
            # Many rapid requests...
            for i in range(1500):
                client.get_estimates(client_id, pickup, dropoff)
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e}")
            # Wait and retry, or implement exponential backoff
        ```
    """
    pass


class ServiceUnavailableError(UberCentralError):
    """
    Raised when the Uber Central API service is temporarily unavailable.
    
    This typically indicates:
    - API server maintenance
    - Temporary outages
    - Upstream Uber API issues
    - Network connectivity problems
    
    Example:
        ```python
        import time
        from uber_central_client.exceptions import ServiceUnavailableError
        
        def retry_with_backoff(func, max_retries=3):
            for attempt in range(max_retries):
                try:
                    return func()
                except ServiceUnavailableError as e:
                    if attempt == max_retries - 1:
                        raise e
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
        ```
    """
    pass


# Convenience function to map HTTP status codes to exceptions
def exception_from_status_code(status_code: int, detail: str) -> UberCentralError:
    """
    Create appropriate exception based on HTTP status code and error detail.
    
    Args:
        status_code: HTTP response status code
        detail: Error detail message from API
        
    Returns:
        Appropriate UberCentralError subclass instance
    """
    if status_code == 401:
        return AuthenticationError(detail)
    elif status_code == 404:
        if "Client not found" in detail:
            return ClientNotFoundError(detail)
        elif "Ride not found" in detail:
            return RideNotFoundError(detail)
        else:
            return UberCentralError(detail)
    elif status_code == 422:
        return ValidationError(detail)
    elif status_code == 429:
        return RateLimitError(detail)
    elif status_code == 503:
        return ServiceUnavailableError(detail)
    elif status_code >= 400 and "failed" in detail.lower():
        return BookingError(detail)
    else:
        return UberCentralError(f"HTTP {status_code}: {detail}")


# Error code mappings for specific Uber API errors
UBER_ERROR_CODES = {
    "invalid_phone_number": ValidationError,
    "invalid_address": ValidationError,
    "schedule_in_the_past": ValidationError,
    "no_drivers_available": BookingError,
    "service_unavailable": ServiceUnavailableError,
    "rate_limited": RateLimitError,
    "authentication_failed": AuthenticationError,
    "client_not_found": ClientNotFoundError,
    "ride_not_found": RideNotFoundError,
}