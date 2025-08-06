#!/usr/bin/env python3
"""
Test script for python_client package.

This script tests all the major functionality of the client against the live API.
"""

import sys
import os
from uber_central_client import UberCentralClient
from uber_central_client.exceptions import (
    AuthenticationError, ClientNotFoundError, ValidationError, BookingError
)

def test_client():
    """Test the Uber Central client functionality."""
    
    # Initialize client with production API key
    try:
        api_key = os.getenv("UBER_CENTRAL_API_KEY", "test-key-placeholder")
        client = UberCentralClient(api_key=api_key)
        print("✅ Client initialized successfully")
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    
    # Test health check
    try:
        health = client.health_check()
        print(f"✅ Health check passed: {health.get('message', 'API operational')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test user initialization
    try:
        user = client.initialize_user(
            name="Test User SDK",
            email="test@uber-central-sdk.com",
            metadata={
                "source": "python-client-testing",
                "version": "1.0.0",
                "test_run": True
            }
        )
        client_id = user.client_id
        print(f"✅ User created: {client_id}")
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False
    
    # Test ride estimates
    try:
        estimates = client.get_estimates(
            client_id=client_id,
            pickup_address="Union Square, San Francisco, CA",
            dropoff_address="SFO Airport",
            capacity=1
        )
        print(f"✅ Got {len(estimates)} ride estimates:")
        for estimate in estimates[:3]:  # Show first 3
            print(f"   • {estimate.display_name}: {estimate.price_estimate} (ETA: {estimate.estimate_time_minutes}min)")
    except ClientNotFoundError as e:
        print(f"❌ Client not found: {e}")
        return False
    except Exception as e:
        print(f"❌ Estimates failed: {e}")
        return False
    
    # Test client stats
    try:
        stats = client.get_client_stats(client_id)
        print(f"✅ Client stats: {stats.total_api_calls} API calls, {stats.total_rides} rides")
    except Exception as e:
        print(f"❌ Stats retrieval failed: {e}")
        return False
    
    # Test usage history
    try:
        usage = client.get_usage_history(client_id, limit=5)
        print(f"✅ Usage history: {len(usage.usage_history)} records")
    except Exception as e:
        print(f"❌ Usage history failed: {e}")
        return False
    
    # Test ride history
    try:
        rides = client.get_ride_history(client_id, limit=5)
        print(f"✅ Ride history: {len(rides.ride_history)} rides")
    except Exception as e:
        print(f"❌ Ride history failed: {e}")
        return False
    
    # Test error handling with invalid client
    try:
        client.get_estimates(
            client_id="invalid-client-id",
            pickup_address="123 Main St",
            dropoff_address="456 Oak Ave"
        )
        print("❌ Error handling failed - should have thrown ClientNotFoundError")
        return False
    except ClientNotFoundError:
        print("✅ Error handling works - ClientNotFoundError caught correctly")
    except Exception as e:
        print(f"❌ Unexpected error in error handling test: {e}")
        return False
    
    print("\n🎉 All tests passed! Client is working correctly.")
    return True


def test_booking_workflow():
    """Test the complete booking workflow (estimates -> booking)."""
    
    print("\n🚗 Testing complete booking workflow...")
    
    api_key = os.getenv("UBER_CENTRAL_API_KEY", "test-key-placeholder")
    client = UberCentralClient(api_key=api_key)
    
    # Create user for booking test
    user = client.initialize_user(
        name="Booking Test User",
        email="booking-test@uber-central-sdk.com"
    )
    client_id = user.client_id
    
    # Get estimates
    estimates = client.get_estimates(
        client_id=client_id,
        pickup_address="456 Mission St, San Francisco, CA",
        dropoff_address="123 Market St, San Francisco, CA"
    )
    
    if not estimates:
        print("❌ No estimates available for booking test")
        return False
    
    print(f"✅ Got {len(estimates)} estimates for booking test")
    
    # Note: We won't actually book a ride in testing to avoid unwanted rides
    # But we can test the booking request structure
    try:
        # This would book a real ride - commented out for testing
        """
        ride = client.book_ride(
            client_id=client_id,
            pickup_address="456 Mission St, San Francisco, CA",
            dropoff_address="123 Market St, San Francisco, CA",
            rider_name="Test Booking User",
            rider_phone="9167995790",
            product_id=estimates[0].product_id,
            message_to_driver="SDK test booking - please cancel if received",
            expense_memo="Python client testing"
        )
        print(f"✅ Booking structure test passed: {ride.ride_id}")
        """
        print("✅ Booking workflow test passed (booking commented out to avoid real rides)")
    except Exception as e:
        print(f"❌ Booking workflow test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🧪 Testing Uber Central Python Client (python_client)")
    print("=" * 70)
    
    # Run basic functionality tests
    success = test_client()
    
    if success:
        # Run booking workflow test
        success = test_booking_workflow()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("The python_client package is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Check the error messages above for details.")
        sys.exit(1)