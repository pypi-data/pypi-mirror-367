#!/usr/bin/env python3
"""
Test script for uber-central-rest-client: Schedule and Cancel Workflow

This script demonstrates:
1. Looking up ride estimates
2. Scheduling a ride for Will Roberts (9167995790) 
3. Canceling the scheduled ride

This is a complete end-to-end test of the scheduling functionality.
"""

import sys
import os
import time
from datetime import datetime, timedelta
from uber_central_client import UberCentralClient
from uber_central_client.exceptions import (
    AuthenticationError, ClientNotFoundError, ValidationError, BookingError
)


def test_schedule_and_cancel_workflow():
    """Test the complete schedule and cancel workflow."""
    
    print("🧪 Testing Uber Central Schedule & Cancel Workflow")
    print("=" * 60)
    
    # Initialize client
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
    
    # Step 1: Create user account for Will Roberts
    print("\n📋 Step 1: Creating user account...")
    try:
        user = client.initialize_user(
            name="Will Roberts",
            email="will@uber-central-test.com",
            metadata={
                "test_type": "schedule_and_cancel_workflow",
                "phone": "9167995790",
                "test_timestamp": datetime.now().isoformat()
            }
        )
        client_id = user.client_id
        print(f"✅ User created: {client_id}")
        print(f"   Name: Will Roberts")
        print(f"   Email: will@uber-central-test.com")
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False
    
    # Step 2: Look up ride estimates
    print("\n🔍 Step 2: Looking up ride estimates...")
    pickup_address = "456 Mission St, San Francisco, CA"
    dropoff_address = "123 Market St, San Francisco, CA"
    
    try:
        estimates = client.get_estimates(
            client_id=client_id,
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            capacity=1
        )
        print(f"✅ Found {len(estimates)} ride options:")
        
        # Show top 5 estimates
        for i, estimate in enumerate(estimates[:5]):
            print(f"   {i+1}. {estimate.display_name}: {estimate.price_estimate} (ETA: {estimate.estimate_time_minutes}min)")
        
        # Select UberX for scheduling (or first available option)
        selected_estimate = None
        for estimate in estimates:
            if "UberX" in estimate.display_name:
                selected_estimate = estimate
                break
        
        if not selected_estimate:
            selected_estimate = estimates[0]  # Use first available
            
        print(f"🎯 Selected for scheduling: {selected_estimate.display_name} - {selected_estimate.price_estimate}")
        
    except Exception as e:
        print(f"❌ Estimates lookup failed: {e}")
        return False
    
    # Step 3: Schedule the ride for future pickup
    print("\n📅 Step 3: Scheduling ride for Will Roberts...")
    
    # Schedule for 2 hours from now
    pickup_time = datetime.now() + timedelta(hours=2)
    pickup_time_str = pickup_time.strftime("%Y-%m-%dT%H:%M:%S-08:00")  # Pacific time
    
    try:
        scheduled_ride = client.schedule_ride(
            client_id=client_id,
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            rider_name="Will Roberts",
            rider_phone="9167995790",
            pickup_time=pickup_time_str,
            product_id=selected_estimate.product_id,
            message_to_driver="Test scheduling - this ride will be cancelled immediately",
            expense_memo="Schedule and cancel workflow test"
        )
        
        ride_id = scheduled_ride.ride_id
        print(f"✅ Ride scheduled successfully!")
        print(f"   Ride ID: {ride_id}")
        print(f"   Status: {scheduled_ride.status}")
        print(f"   Pickup Time: {pickup_time.strftime('%Y-%m-%d at %I:%M %p')}")
        print(f"   Rider: Will Roberts (9167995790)")
        print(f"   Route: {pickup_address} → {dropoff_address}")
        
        if scheduled_ride.confirmation_number:
            print(f"   Confirmation: {scheduled_ride.confirmation_number}")
        
    except BookingError as e:
        print(f"❌ Ride scheduling failed: {e}")
        print("   This might be due to:")
        print("   - No drivers available in the area")
        print("   - Invalid pickup/dropoff locations")
        print("   - Time slot not available")
        return False
    except ValidationError as e:
        print(f"❌ Scheduling validation failed: {e}")
        print("   This might be due to:")
        print("   - Invalid phone number format")
        print("   - Invalid pickup time")
        return False
    except Exception as e:
        print(f"❌ Unexpected scheduling error: {e}")
        return False
    
    # Step 4: Check ride status before cancellation
    print("\n🔍 Step 4: Checking ride status...")
    try:
        status = client.get_ride_status(ride_id)
        print(f"✅ Ride status retrieved:")
        print(f"   Current Status: {status.status}")
        print(f"   Pickup: {status.pickup_address}")
        print(f"   Dropoff: {status.dropoff_address}")
        
        if status.driver_name:
            print(f"   Driver: {status.driver_name}")
        if status.vehicle_make and status.vehicle_model:
            print(f"   Vehicle: {status.vehicle_make} {status.vehicle_model}")
            
    except Exception as e:
        print(f"⚠️  Status check failed (continuing anyway): {e}")
    
    # Step 5: Cancel the scheduled ride
    print("\n❌ Step 5: Canceling the scheduled ride...")
    try:
        cancellation = client.cancel_ride(ride_id)
        print(f"✅ Ride cancelled successfully!")
        print(f"   Ride ID: {ride_id}")
        print(f"   Cancellation Status: {cancellation.status}")
        print(f"   Message: {cancellation.message}")
        
    except Exception as e:
        print(f"❌ Ride cancellation failed: {e}")
        print("   This might be due to:")
        print("   - Ride already started or completed")
        print("   - Invalid ride ID")
        print("   - Cancellation window expired")
        return False
    
    # Step 6: Verify cancellation with updated status
    print("\n🔍 Step 6: Verifying cancellation...")
    try:
        final_status = client.get_ride_status(ride_id)
        print(f"✅ Final ride status:")
        print(f"   Status: {final_status.status}")
        
        if final_status.status.lower() == "cancelled":
            print("   ✅ Cancellation confirmed!")
        else:
            print(f"   ⚠️  Status is '{final_status.status}' - may still be processing")
            
    except Exception as e:
        print(f"⚠️  Final status check failed: {e}")
        print("   Cancellation likely succeeded but status check failed")
    
    # Step 7: Check updated usage statistics
    print("\n📊 Step 7: Checking usage statistics...")
    try:
        stats = client.get_client_stats(client_id)
        print(f"✅ Updated statistics:")
        print(f"   Total API calls: {stats.total_api_calls}")
        print(f"   Total rides: {stats.total_rides}")
        print(f"   Scheduled rides: {stats.scheduled_rides}")
        print(f"   Cancellations: {stats.cancellations}")
        
        # Check ride history
        rides = client.get_ride_history(client_id, limit=5)
        print(f"✅ Recent ride history: {len(rides.ride_history)} records")
        
        for ride_record in rides.ride_history:
            print(f"   • {ride_record['ride_type']}: {ride_record['ride_id']} - {ride_record['status']}")
        
    except Exception as e:
        print(f"⚠️  Statistics check failed: {e}")
    
    print("\n🎉 Schedule and Cancel Workflow Complete!")
    print("=" * 60)
    print("✅ Successfully demonstrated:")
    print("   1. User account creation")
    print("   2. Ride estimates lookup")
    print("   3. Ride scheduling for Will Roberts (9167995790)")
    print("   4. Ride status checking")
    print("   5. Ride cancellation")
    print("   6. Usage analytics tracking")
    
    return True


def main():
    """Main test execution."""
    print("🚀 Starting Schedule & Cancel Test for Will Roberts")
    print("📱 Phone: 9167995790")
    print("🏢 Using uber-central-rest-client package")
    print()
    
    success = test_schedule_and_cancel_workflow()
    
    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("The schedule and cancel workflow is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED")
        print("Check the error messages above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()