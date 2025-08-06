"""
Uber Central REST API Client

A Python client library for the Uber Central API that provides enterprise-grade 
Uber ride management capabilities with user tracking and comprehensive analytics.

Example:
    ```python
    from uber_central_client import UberCentralClient
    
    # Initialize client
    client = UberCentralClient(api_key="your-api-key")
    
    # Create user account
    user = client.initialize_user(name="John Doe", email="john@company.com")
    client_id = user.client_id
    
    # Get ride estimates
    estimates = client.get_estimates(
        client_id=client_id,
        pickup_address="Union Square, San Francisco, CA",
        dropoff_address="SFO Airport"
    )
    
    # Book immediate ride
    ride = client.book_ride(
        client_id=client_id,
        pickup_address="Union Square, San Francisco, CA", 
        dropoff_address="SFO Airport",
        rider_name="John Doe",
        rider_phone="9167995790"
    )
    ```
"""

from .client import UberCentralClient
from .models import (
    # Request models
    InitializeUserRequest,
    EstimateRequest,
    BookRideRequest,
    ScheduleRideRequest,
    
    # Response models
    InitializeUserResponse,
    RideEstimate,
    RideResponse,
    RideStatusResponse,
    ClientStats,
    UsageHistory,
    RideHistory,
    
    # Constants
    RideStatus,
    RideType,
    VehicleTypes,
    
    # Validators
    validate_phone_number,
    validate_client_id,
)
from .exceptions import (
    UberCentralError,
    AuthenticationError,
    ClientNotFoundError,
    RideNotFoundError,
    ValidationError,
    BookingError,
    RateLimitError,
    ServiceUnavailableError,
)

# Package metadata
__version__ = "1.1.0"
__author__ = "Uber Central Team"
__email__ = "support@uber-central.com"
__description__ = "Official Python client for the Uber Central API"
__url__ = "https://github.com/lymanlabs/uber-central"

# Main exports - these are the primary classes developers will use
__all__ = [
    # Main client class
    "UberCentralClient",
    
    # Data models
    "InitializeUserRequest",
    "EstimateRequest", 
    "BookRideRequest",
    "ScheduleRideRequest",
    "InitializeUserResponse",
    "RideEstimate",
    "RideResponse",
    "RideStatusResponse",
    "ClientStats",
    "UsageHistory",
    "RideHistory",
    
    # Constants and enums
    "RideStatus",
    "RideType", 
    "VehicleTypes",
    
    # Utility functions
    "validate_phone_number",
    "validate_client_id",
    
    # Exceptions
    "UberCentralError",
    "AuthenticationError",
    "ClientNotFoundError",
    "RideNotFoundError",
    "ValidationError",
    "BookingError",
    "RateLimitError",
    "ServiceUnavailableError",
]

# Package-level convenience functions
def create_client(api_key: str, **kwargs) -> UberCentralClient:
    """
    Convenience function to create a new UberCentralClient instance.
    
    Args:
        api_key: Your Uber Central API key
        **kwargs: Additional client configuration options
        
    Returns:
        Configured UberCentralClient instance
        
    Example:
        ```python
        import uber_central_client
        
        client = uber_central_client.create_client(
            api_key="your-api-key",
            timeout=60
        )
        ```
    """
    return UberCentralClient(api_key=api_key, **kwargs)


def get_version() -> str:
    """
    Get the current package version.
    
    Returns:
        Version string
    """
    return __version__


# Package initialization check
def _check_dependencies():
    """Check that required dependencies are available."""
    try:
        import requests
        import pydantic
    except ImportError as e:
        missing_dep = str(e).split("'")[1]
        raise ImportError(
            f"Missing required dependency: {missing_dep}. "
            f"Please install it with: pip install {missing_dep}"
        )

# Run dependency check on import
_check_dependencies()