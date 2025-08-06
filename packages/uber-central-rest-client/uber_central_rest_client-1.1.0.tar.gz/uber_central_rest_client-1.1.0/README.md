# 🚗 Uber Central REST Client

[![PyPI version](https://badge.fury.io/py/uber-central-rest-client.svg)](https://badge.fury.io/py/uber-central-rest-client)
[![Python Support](https://img.shields.io/pypi/pyversions/uber-central-rest-client.svg)](https://pypi.org/project/uber-central-rest-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-API%20Reference-blue)](https://apparel-scraper--uber-central-api-serve.modal.run/docs)

**Official Python client for the Uber Central API** - Enterprise-grade Uber ride management with comprehensive user tracking, usage analytics, and audit trails.

## ✨ Features

- 🔑 **Simple Authentication** - Single API key setup
- 👥 **User Management** - Client account system with unique identifiers
- 💰 **Ride Estimates** - Get prices for all vehicle types (UberX, Comfort, Black, etc.)
- 🚗 **Immediate Booking** - Book rides for immediate pickup
- 📅 **Scheduled Rides** - Schedule rides for future pickup (up to 30 days)
- 📊 **Usage Analytics** - Comprehensive usage tracking and ride history
- 🔍 **Ride Management** - Real-time status tracking and cancellation
- 🛡️ **Enterprise Ready** - Full audit trails, expense tracking, and compliance features
- 🎯 **Type Safe** - Full type hints and Pydantic models
- ⚡ **Easy Integration** - Simple, intuitive API

## 🚀 Quick Start

### Installation

```bash
pip install uber-central-rest-client
```

### Basic Usage

```python
from uber_central_client import UberCentralClient

# Initialize client
client = UberCentralClient(api_key="your-api-key")

# Create user account
user = client.initialize_user(
    name="John Doe",
    email="john@company.com",
    metadata={"department": "Sales", "cost_center": "SC-100"}
)
client_id = user.client_id

# Get ride estimates
estimates = client.get_estimates(
    client_id=client_id,
    pickup_address="Union Square, San Francisco, CA",
    dropoff_address="SFO Airport"
)

print("Available rides:")
for estimate in estimates:
    print(f"  {estimate.display_name}: {estimate.price_estimate}")

# Book immediate ride
ride = client.book_ride(
    client_id=client_id,
    pickup_address="Union Square, San Francisco, CA", 
    dropoff_address="SFO Airport",
    rider_name="John Doe",
    rider_phone="9167995790",
    message_to_driver="Terminal 3 pickup"
)

print(f"Ride booked! ID: {ride.ride_id}")
```

## 📋 API Reference

### 🔧 Client Initialization

```python
from uber_central_client import UberCentralClient

client = UberCentralClient(
    api_key="your-api-key",
    base_url="https://apparel-scraper--uber-central-api-serve.modal.run",  # optional
    timeout=30  # optional
)
```

### 👥 User Management

```python
# Create new user account
user = client.initialize_user(
    name="Alice Johnson",           # optional
    email="alice@company.com",      # optional
    metadata={                      # optional
        "department": "Marketing",
        "cost_center": "MC-200",
        "manager": "Bob Smith"
    }
)
client_id = user.client_id  # Save this for all future requests
```

### 💰 Get Ride Estimates

```python
estimates = client.get_estimates(
    client_id="your-client-id",
    pickup_address="123 Main St, San Francisco, CA",
    dropoff_address="456 Market St, San Francisco, CA",
    capacity=2  # optional, default: 1
)

# Available vehicle types: UberX, Comfort, UberXL, Black, Black SUV, Green, etc.
for estimate in estimates:
    print(f"{estimate.display_name}: {estimate.price_estimate} "
          f"(ETA: {estimate.estimate_time_minutes} min)")
```

### 🚗 Book Immediate Ride

```python
ride = client.book_ride(
    client_id="your-client-id",
    pickup_address="123 Main St, San Francisco, CA",
    dropoff_address="456 Market St, San Francisco, CA",
    rider_name="John Doe",
    rider_phone="9167995790",
    product_id="uber-x-product-id",           # optional - from estimates
    message_to_driver="Main entrance pickup", # optional
    expense_memo="Client meeting transport"   # optional
)

print(f"Ride booked: {ride.ride_id}")
```

### 📅 Schedule Future Ride

```python
from datetime import datetime, timedelta

# Schedule ride for 2 hours from now
pickup_time = datetime.now() + timedelta(hours=2)

ride = client.schedule_ride(
    client_id="your-client-id",
    pickup_address="SFO Airport Terminal 3",
    dropoff_address="123 Main St, San Francisco, CA",
    rider_name="Jane Doe",
    rider_phone="9167995790",
    pickup_time=pickup_time,  # or ISO string: "2025-08-05T14:30:00-07:00"
    message_to_driver="Flight AA 1234 arrival"
)
```

### 🔍 Ride Management

```python
# Get ride status
status = client.get_ride_status("ride-id")
print(f"Status: {status.status}")
print(f"Driver: {status.driver_name}")

# Cancel ride
result = client.cancel_ride("ride-id")
print(f"Cancelled: {result.status}")
```

### 📊 Analytics & Reporting

```python
# Get client usage statistics
stats = client.get_client_stats("client-id")
print(f"Total rides: {stats.total_rides}")
print(f"API calls: {stats.total_api_calls}")

# Get detailed usage history
usage = client.get_usage_history("client-id", limit=50)
for record in usage.usage_history:
    print(f"{record['endpoint']} at {record['timestamp']}")

# Get ride history
rides = client.get_ride_history("client-id", limit=25)
for ride in rides.ride_history:
    print(f"Ride {ride['ride_id']}: {ride['pickup_address']} → {ride['dropoff_address']}")
```

## 🏢 Enterprise Features

### User Management & Tracking
- **Client ID System** - Unique identifiers for each user/department
- **Flexible Metadata** - Store custom fields (department, cost center, etc.)
- **Usage Analytics** - Track API calls, ride patterns, and costs
- **Audit Trails** - Complete history of all operations

### Expense & Compliance
- **Expense Memos** - Attach internal tracking notes to rides
- **Driver Messages** - Special instructions for drivers
- **Complete History** - All ride details stored permanently
- **Usage Reporting** - Detailed analytics for expense reporting

### Safety & Control
- **No Unwanted Calls** - Automatic calling disabled by default
- **SMS Notifications** - Riders receive booking confirmations
- **Driver Verification** - All rides through verified Uber platform
- **Cancellation Control** - Easy ride cancellation with policy compliance

## 🛠️ Error Handling

The client provides specific exception types for different error scenarios:

```python
from uber_central_client import (
    UberCentralClient, 
    AuthenticationError, 
    ClientNotFoundError,
    ValidationError,
    BookingError
)

try:
    client = UberCentralClient(api_key="invalid-key")
except AuthenticationError:
    print("Invalid API key")

try:
    estimates = client.get_estimates(
        client_id="invalid-client",
        pickup_address="123 Main St",
        dropoff_address="456 Oak Ave"
    )
except ClientNotFoundError:
    print("Client not found - call initialize_user() first")
except ValidationError as e:
    print(f"Invalid request: {e}")
except BookingError as e:
    print(f"Booking failed: {e}")
```

### Exception Types
- **`AuthenticationError`** - Invalid API key
- **`ClientNotFoundError`** - Invalid client_id
- **`RideNotFoundError`** - Invalid ride_id
- **`ValidationError`** - Invalid request parameters
- **`BookingError`** - Ride booking/scheduling failures
- **`RateLimitError`** - API rate limits exceeded
- **`ServiceUnavailableError`** - Temporary service issues

## 🔧 Advanced Usage

### Custom Configuration

```python
from uber_central_client import UberCentralClient

# Custom timeouts and base URL
client = UberCentralClient(
    api_key="your-api-key",
    base_url="https://your-custom-domain.com",
    timeout=60  # 60 second timeout
)

# Health check
health = client.health_check()
print(f"API Status: {health.get('status')}")
```

### Batch Operations

```python
# Create multiple users
users = []
for i in range(5):
    user = client.initialize_user(
        name=f"User {i}",
        metadata={"batch": "onboarding-2025"}
    )
    users.append(user.client_id)

# Get estimates for multiple locations
locations = [
    ("Downtown", "Airport"),
    ("Office", "Hotel"),
    ("Station", "Mall")
]

for pickup, dropoff in locations:
    estimates = client.get_estimates(
        client_id=users[0],
        pickup_address=pickup,
        dropoff_address=dropoff
    )
    print(f"{pickup} → {dropoff}: {len(estimates)} options")
```

### Vehicle Type Selection

```python
from uber_central_client import VehicleTypes

estimates = client.get_estimates(client_id, pickup, dropoff)

# Find specific vehicle types
uberx_estimate = next(
    (est for est in estimates if est.display_name == VehicleTypes.UBER_X), 
    None
)

comfort_estimate = next(
    (est for est in estimates if est.display_name == VehicleTypes.COMFORT), 
    None
)

if uberx_estimate:
    print(f"UberX: {uberx_estimate.price_estimate}")
if comfort_estimate:
    print(f"Comfort: {comfort_estimate.price_estimate}")
```

## 📚 Complete Examples

### Corporate Booking System

```python
from uber_central_client import UberCentralClient
from datetime import datetime, timedelta

class CorporateRideManager:
    def __init__(self, api_key):
        self.client = UberCentralClient(api_key)
        
    def onboard_employee(self, name, email, department, cost_center):
        """Create new employee account."""
        user = self.client.initialize_user(
            name=name,
            email=email,
            metadata={
                "department": department,
                "cost_center": cost_center,
                "onboarded_at": datetime.now().isoformat()
            }
        )
        return user.client_id
    
    def book_airport_ride(self, client_id, employee_name, phone, flight_info):
        """Book airport pickup with flight details."""
        ride = self.client.book_ride(
            client_id=client_id,
            pickup_address="SFO Airport",
            dropoff_address="123 Office St, San Francisco, CA",
            rider_name=employee_name,
            rider_phone=phone,
            message_to_driver=f"Flight pickup: {flight_info}",
            expense_memo=f"Airport pickup - {flight_info}"
        )
        return ride.ride_id
    
    def generate_usage_report(self, client_id):
        """Generate usage report for employee."""
        stats = self.client.get_client_stats(client_id)
        usage = self.client.get_usage_history(client_id)
        rides = self.client.get_ride_history(client_id)
        
        return {
            "summary": stats,
            "detailed_usage": usage,
            "ride_history": rides
        }

# Usage
manager = CorporateRideManager("your-api-key")

# Onboard new employee
client_id = manager.onboard_employee(
    name="Alice Johnson",
    email="alice@company.com", 
    department="Sales",
    cost_center="SALES-2025"
)

# Book airport ride
ride_id = manager.book_airport_ride(
    client_id=client_id,
    employee_name="Alice Johnson",
    phone="9167995790",
    flight_info="United Airlines UA 123"
)

# Generate monthly report
report = manager.generate_usage_report(client_id)
```

## 🔗 Related Resources

- **📖 API Documentation**: https://apparel-scraper--uber-central-api-serve.modal.run/docs
- **🌐 Live API**: https://apparel-scraper--uber-central-api-serve.modal.run
- **📁 GitHub Repository**: https://github.com/lymanlabs/uber-central
- **🐛 Issue Tracker**: https://github.com/lymanlabs/uber-central/issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Documentation**: Check the [API Reference](https://apparel-scraper--uber-central-api-serve.modal.run/docs)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/lymanlabs/uber-central/issues)  
- **Questions**: Contact support@uber-central.com

## 🎯 Changelog

### v1.0.0 (2025-01-04)
- Initial release
- Complete API client implementation
- Full type safety with Pydantic models
- Comprehensive error handling
- Enterprise features (user management, analytics, audit trails)
- Production-ready with extensive testing

---

**🚀 Ready to integrate enterprise Uber ride management into your application!**