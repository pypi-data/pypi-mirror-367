"""
Uber Central REST API Client

A Python client library for the Uber Central API that provides enterprise-grade 
Uber ride management capabilities with user tracking and comprehensive analytics.
"""

import requests
import time
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

from .models import (
    InitializeUserRequest, InitializeUserResponse,
    EstimateRequest, RideEstimate,
    BookRideRequest, ScheduleRideRequest, RideResponse,
    RideStatusResponse, ClientStats, UsageHistory, RideHistory
)
from .exceptions import (
    UberCentralError, AuthenticationError, ClientNotFoundError,
    RideNotFoundError, BookingError, ValidationError
)


class UberCentralClient:
    """
    Official Python client for the Uber Central API.
    
    Provides complete Uber ride management with enterprise features:
    - User management with client_id system
    - Ride estimates across all vehicle types
    - Immediate and scheduled ride booking
    - Comprehensive usage analytics and audit trails
    - Real-time ride status tracking
    
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
    
    def __init__(
        self, 
        api_key: str,
        base_url: str = "https://apparel-scraper--uber-central-api-serve.modal.run",
        timeout: int = 30
    ):
        """
        Initialize the Uber Central API client.
        
        Args:
            api_key: Your Uber Central API key
            base_url: API base URL (defaults to production endpoint)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"uber-central-rest-client/1.0.0"
        }
        
        # Test authentication on initialization
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test API connectivity and authentication."""
        try:
            response = requests.get(
                f"{self.base_url}/",
                headers=self.headers,
                timeout=self.timeout
            )
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code != 200:
                raise UberCentralError(f"API connection failed: {response.status_code}")
        except requests.RequestException as e:
            raise UberCentralError(f"Connection error: {str(e)}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API with error handling.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: URL parameters
            
        Returns:
            Parsed JSON response
            
        Raises:
            Various UberCentralError subclasses based on response
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=self.timeout
            )
            
            # Handle common error status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 404:
                error_detail = response.json().get("detail", "Not found")
                if "Client not found" in error_detail:
                    raise ClientNotFoundError(error_detail)
                elif "Ride not found" in error_detail:
                    raise RideNotFoundError(error_detail)
                else:
                    raise UberCentralError(error_detail)
            elif response.status_code == 422:
                error_detail = response.json().get("detail", "Validation error")
                raise ValidationError(error_detail)
            elif response.status_code >= 400:
                error_detail = response.json().get("detail", f"HTTP {response.status_code}")
                if "failed" in error_detail.lower():
                    raise BookingError(error_detail)
                else:
                    raise UberCentralError(error_detail)
            
            return response.json()
            
        except requests.RequestException as e:
            raise UberCentralError(f"Request failed: {str(e)}")
    
    # User Management
    
    def initialize_user(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> InitializeUserResponse:
        """
        Create a new client account and return client_id for API access.
        
        Args:
            name: User's full name
            email: User's email address
            metadata: Custom metadata (department, cost center, etc.)
            
        Returns:
            InitializeUserResponse with client_id and account details
            
        Example:
            ```python
            user = client.initialize_user(
                name="Alice Johnson",
                email="alice@company.com", 
                metadata={"department": "Sales", "cost_center": "SC-100"}
            )
            client_id = user.client_id
            ```
        """
        request_data = {}
        if name:
            request_data["name"] = name
        if email:
            request_data["email"] = email
        if metadata:
            request_data["metadata"] = metadata
            
        response = self._make_request("POST", "/api/v1/initialize_user", request_data)
        return InitializeUserResponse(**response)
    
    # Ride Estimates
    
    def get_estimates(
        self,
        client_id: str,
        pickup_address: str,
        dropoff_address: str,
        capacity: int = 1
    ) -> List[RideEstimate]:
        """
        Get ride price estimates for all available vehicle types.
        
        Works for both immediate and scheduled rides - pricing is the same.
        Each estimate includes an 'available' field indicating if the vehicle
        type supports scheduling.
        
        Args:
            client_id: Valid client identifier from initialize_user
            pickup_address: Starting location (address, landmark, coordinates)
            dropoff_address: Destination location
            capacity: Number of passengers (default: 1)
            
        Returns:
            List of RideEstimate objects for all available vehicle types
            
        Example:
            ```python
            estimates = client.get_estimates(
                client_id="abc-123-def-456",
                pickup_address="Union Square, San Francisco, CA",
                dropoff_address="SFO Airport",
                capacity=2
            )
            
            for estimate in estimates:
                print(f"{estimate.display_name}: {estimate.price_estimate}")
                # Check if schedulable: estimate.available
            ```
        """
        request_data = {
            "client_id": client_id,
            "pickup_address": pickup_address,
            "dropoff_address": dropoff_address,
            "capacity": capacity
        }
        
        response = self._make_request("POST", "/api/v1/estimates", request_data)
        return [RideEstimate(**estimate) for estimate in response]
    
    def get_scheduled_estimates(
        self,
        client_id: str,
        pickup_address: str,
        dropoff_address: str,
        capacity: int = 1
    ) -> List[RideEstimate]:
        """
        Get price estimates for scheduled rides (up to 30 days in advance).
        
        This is a convenience method that calls the scheduled estimates endpoint.
        The pricing is identical to immediate rides, but provides clarity that
        you're checking prices for a future scheduled ride.
        
        Args:
            client_id: Valid client identifier from initialize_user
            pickup_address: Starting location (address, landmark, coordinates)
            dropoff_address: Destination location
            capacity: Number of passengers (default: 1)
            
        Returns:
            List of RideEstimate objects with scheduling availability
            
        Example:
            ```python
            # Check prices for a scheduled ride
            estimates = client.get_scheduled_estimates(
                client_id="abc-123-def-456",
                pickup_address="Union Square, San Francisco, CA",
                dropoff_address="SFO Airport",
                capacity=2
            )
            
            # Find schedulable options
            schedulable = [e for e in estimates if e.available]
            print(f"Found {len(schedulable)} vehicle types that support scheduling")
            ```
        """
        request_data = {
            "client_id": client_id,
            "pickup_address": pickup_address,
            "dropoff_address": dropoff_address,
            "capacity": capacity
        }
        
        response = self._make_request("POST", "/api/v1/estimates/scheduled", request_data)
        return [RideEstimate(**estimate) for estimate in response]
    
    # Ride Booking
    
    def book_ride(
        self,
        client_id: str,
        pickup_address: str,
        dropoff_address: str,
        rider_name: str,
        rider_phone: str,
        product_id: Optional[str] = None,
        message_to_driver: Optional[str] = None,
        expense_memo: Optional[str] = None
    ) -> RideResponse:
        """
        Book an immediate Uber ride.
        
        Args:
            client_id: Valid client identifier
            pickup_address: Pickup location
            dropoff_address: Destination location
            rider_name: Passenger's full name
            rider_phone: Passenger's phone number (10 digits)
            product_id: Specific vehicle type ID from estimates (optional)
            message_to_driver: Special instructions for driver
            expense_memo: Internal expense tracking note
            
        Returns:
            RideResponse with ride_id and booking details
            
        Example:
            ```python
            ride = client.book_ride(
                client_id="abc-123-def-456",
                pickup_address="123 Market St, San Francisco, CA",
                dropoff_address="456 Mission St, San Francisco, CA", 
                rider_name="John Doe",
                rider_phone="9167995790",
                message_to_driver="Business meeting pickup - main entrance"
            )
            
            print(f"Ride booked! ID: {ride.ride_id}")
            ```
        """
        request_data = {
            "client_id": client_id,
            "pickup_address": pickup_address,
            "dropoff_address": dropoff_address,
            "rider_name": rider_name,
            "rider_phone": rider_phone
        }
        
        if product_id:
            request_data["product_id"] = product_id
        if message_to_driver:
            request_data["message_to_driver"] = message_to_driver
        if expense_memo:
            request_data["expense_memo"] = expense_memo
            
        response = self._make_request("POST", "/api/v1/rides/book", request_data)
        return RideResponse(**response)
    
    def schedule_ride(
        self,
        client_id: str,
        pickup_address: str,
        dropoff_address: str,
        rider_name: str,
        rider_phone: str,
        pickup_time: Union[str, datetime],
        product_id: Optional[str] = None,
        message_to_driver: Optional[str] = None,
        expense_memo: Optional[str] = None
    ) -> RideResponse:
        """
        Schedule an Uber ride for future pickup.
        
        Args:
            client_id: Valid client identifier
            pickup_address: Pickup location
            dropoff_address: Destination location
            rider_name: Passenger's full name
            rider_phone: Passenger's phone number
            pickup_time: Pickup time (ISO 8601 string or datetime object)
            product_id: Specific vehicle type ID (optional)
            message_to_driver: Special instructions for driver
            expense_memo: Internal expense tracking note
            
        Returns:
            RideResponse with ride_id and scheduling details
            
        Example:
            ```python
            from datetime import datetime, timedelta
            
            # Schedule ride for 2 hours from now
            pickup_time = datetime.now() + timedelta(hours=2)
            
            ride = client.schedule_ride(
                client_id="abc-123-def-456",
                pickup_address="SFO Airport Terminal 3",
                dropoff_address="123 Market St, San Francisco, CA",
                rider_name="Jane Doe", 
                rider_phone="9167995790",
                pickup_time=pickup_time,
                message_to_driver="Flight arrival pickup - AA 1234"
            )
            ```
        """
        # Convert datetime to ISO string if needed
        if isinstance(pickup_time, datetime):
            pickup_time = pickup_time.isoformat()
            
        request_data = {
            "client_id": client_id,
            "pickup_address": pickup_address,
            "dropoff_address": dropoff_address,
            "rider_name": rider_name,
            "rider_phone": rider_phone,
            "pickup_time": pickup_time
        }
        
        if product_id:
            request_data["product_id"] = product_id
        if message_to_driver:
            request_data["message_to_driver"] = message_to_driver
        if expense_memo:
            request_data["expense_memo"] = expense_memo
            
        response = self._make_request("POST", "/api/v1/rides/schedule", request_data)
        return RideResponse(**response)
    
    # Ride Management
    
    def get_ride_status(self, ride_id: str) -> RideStatusResponse:
        """
        Get current ride status and details.
        
        Args:
            ride_id: Unique ride identifier from booking response
            
        Returns:
            RideStatusResponse with current ride information
            
        Example:
            ```python
            status = client.get_ride_status("b3570825-64d3-4955-b681-591bdb31fdc9")
            print(f"Ride status: {status.status}")
            print(f"Driver: {status.driver_name}")
            ```
        """
        response = self._make_request("GET", f"/api/v1/rides/{ride_id}")
        return RideStatusResponse(**response)
    
    def cancel_ride(self, ride_id: str) -> RideResponse:
        """
        Cancel an existing ride.
        
        Args:
            ride_id: Unique ride identifier from booking response
            
        Returns:
            RideResponse with cancellation confirmation
            
        Example:
            ```python
            result = client.cancel_ride("b3570825-64d3-4955-b681-591bdb31fdc9")
            print(f"Cancellation status: {result.status}")
            ```
        """
        response = self._make_request("DELETE", f"/api/v1/rides/{ride_id}")
        return RideResponse(**response)
    
    # Analytics & Reporting
    
    def get_client_stats(self, client_id: str) -> ClientStats:
        """
        Get usage statistics for a specific client.
        
        Args:
            client_id: Valid client identifier
            
        Returns:
            ClientStats with aggregated usage information
            
        Example:
            ```python
            stats = client.get_client_stats("abc-123-def-456")
            print(f"Total rides: {stats.total_rides}")
            print(f"API calls: {stats.total_api_calls}")
            ```
        """
        response = self._make_request("GET", f"/api/v1/users/{client_id}/stats")
        return ClientStats(**response)
    
    def get_usage_history(
        self, 
        client_id: str, 
        limit: int = 100
    ) -> UsageHistory:
        """
        Get detailed usage history for a specific client.
        
        Args:
            client_id: Valid client identifier
            limit: Maximum records to return (default: 100)
            
        Returns:
            UsageHistory with detailed API call logs
            
        Example:
            ```python
            usage = client.get_usage_history("abc-123-def-456", limit=50)
            for record in usage.usage_history:
                print(f"{record['endpoint']} at {record['timestamp']}")
            ```
        """
        params = {"limit": limit}
        response = self._make_request("GET", f"/api/v1/users/{client_id}/usage", params=params)
        return UsageHistory(**response)
    
    def get_ride_history(
        self, 
        client_id: str, 
        limit: int = 100
    ) -> RideHistory:
        """
        Get ride history for a specific client.
        
        Args:
            client_id: Valid client identifier
            limit: Maximum records to return (default: 100)
            
        Returns:
            RideHistory with detailed ride booking logs
            
        Example:
            ```python
            rides = client.get_ride_history("abc-123-def-456", limit=25)
            for ride in rides.ride_history:
                print(f"Ride {ride['ride_id']}: {ride['pickup_address']} → {ride['dropoff_address']}")
            ```
        """
        params = {"limit": limit}
        response = self._make_request("GET", f"/api/v1/users/{client_id}/rides", params=params)
        return RideHistory(**response)
    
    # Utility Methods
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API service health and connectivity.
        
        Returns:
            Health status information
            
        Example:
            ```python
            health = client.health_check()
            print(f"API Status: {health.get('status', 'unknown')}")
            ```
        """
        return self._make_request("GET", "/")