"""
Data models and type definitions for the Uber Central API client.

These Pydantic models provide type safety and validation for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


# Request Models

class InitializeUserRequest(BaseModel):
    """Request model for creating a new user account."""
    name: Optional[str] = None
    email: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class EstimateRequest(BaseModel):
    """Request model for getting ride estimates."""
    client_id: str
    pickup_address: str
    dropoff_address: str
    capacity: int = 1


class BookRideRequest(BaseModel):
    """Request model for booking an immediate ride."""
    client_id: str
    pickup_address: str
    dropoff_address: str
    rider_name: str
    rider_phone: str
    product_id: Optional[str] = None
    message_to_driver: Optional[str] = None
    expense_memo: Optional[str] = None


class ScheduleRideRequest(BaseModel):
    """Request model for scheduling a future ride."""
    client_id: str
    pickup_address: str
    dropoff_address: str
    rider_name: str
    rider_phone: str
    pickup_time: str
    product_id: Optional[str] = None
    message_to_driver: Optional[str] = None
    expense_memo: Optional[str] = None


# Response Models

class InitializeUserResponse(BaseModel):
    """Response model for user initialization."""
    success: bool
    client_id: Optional[str] = None
    created_at: Optional[str] = None
    message: str
    metadata: Optional[Dict[str, Any]] = None


class RideEstimate(BaseModel):
    """Model for individual ride estimate."""
    product_id: str
    display_name: str
    price_estimate: str
    estimate_time_minutes: int
    surge_multiplier: float
    available: bool


class RideResponse(BaseModel):
    """Response model for ride booking and scheduling."""
    ride_id: str
    status: str
    confirmation_number: Optional[str] = None
    estimated_arrival: Optional[str] = None
    pickup_time: Optional[str] = None
    message: str


class RideStatusResponse(BaseModel):
    """Response model for ride status queries."""
    ride_id: str
    status: str
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    pickup_address: str
    dropoff_address: str


class ClientStats(BaseModel):
    """Response model for client usage statistics."""
    client_id: str
    total_api_calls: int
    total_rides: int
    immediate_bookings: int
    scheduled_rides: int
    cancellations: int


class UsageRecord(BaseModel):
    """Model for individual usage history record."""
    id: int
    client_id: str
    endpoint: str
    timestamp: str
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    success: bool
    execution_time_ms: Optional[int] = None


class UsageHistory(BaseModel):
    """Response model for usage history."""
    client_id: str
    usage_history: List[Dict[str, Any]]  # Using Dict to allow flexible structure
    total_records: int


class RideRecord(BaseModel):
    """Model for individual ride history record."""
    id: int
    client_id: str
    ride_type: str
    timestamp: str
    ride_id: str
    pickup_address: str
    dropoff_address: str
    rider_name: str
    rider_phone: str
    pickup_time: Optional[str] = None
    product_type: Optional[str] = None
    message_to_driver: Optional[str] = None
    expense_memo: Optional[str] = None
    status: str
    confirmation_number: Optional[str] = None
    full_data: Dict[str, Any]


class RideHistory(BaseModel):
    """Response model for ride history."""
    client_id: str
    ride_history: List[Dict[str, Any]]  # Using Dict to allow flexible structure
    total_records: int


# Utility Models

class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: Optional[str] = None
    timestamp: Optional[str] = None


# Enums and Constants

class RideStatus:
    """Constants for ride status values."""
    PENDING = "pending"
    DRIVER_ASSIGNED = "driver_assigned"
    ARRIVED = "arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class RideType:
    """Constants for ride type values."""
    BOOKING = "booking"
    SCHEDULING = "scheduling"
    CANCELLATION = "cancellation"
    MODIFICATION = "modification"


class VehicleTypes:
    """Common vehicle type display names."""
    UBER_X = "UberX"
    COMFORT = "Comfort"
    UBER_XL = "UberXL"
    BLACK = "Black"
    BLACK_SUV = "Black SUV"
    GREEN = "Green"
    WAIT_SAVE = "Wait & Save"
    POOL = "Pool"
    
    # Premium options
    BLACK_SUV_HOURLY = "Black SUV Hourly"
    BLACK_HOURLY = "Black Hourly"
    
    # Specialty options
    CONNECT = "Connect"
    ASSIST = "Assist"
    WAV = "WAV"  # Wheelchair Accessible Vehicle


# Validation helpers

def validate_phone_number(phone: str) -> bool:
    """
    Validate US phone number format.
    
    Args:
        phone: Phone number string
        
    Returns:
        True if valid 10-digit US phone number
    """
    # Remove common formatting
    clean_phone = ''.join(filter(str.isdigit, phone))
    return len(clean_phone) == 10


def validate_client_id(client_id: str) -> bool:
    """
    Validate client_id format (UUID-like).
    
    Args:
        client_id: Client identifier
        
    Returns:
        True if valid UUID format
    """
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, client_id.lower()))