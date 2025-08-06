#!/usr/bin/env python3
"""
Uber Central MCP Server

This MCP server provides access to the Uber Central API functionality through MCP tools.
It allows LLMs to interact with the Uber Central service to initialize users, get ride estimates,
book rides, schedule rides, and manage ride bookings.

Usage:
    python uber_central_mcp_server.py

The server exposes these tools:
- initialize_user: Create a new client account
- get_estimates: Get ride price estimates for all available vehicle types
- book_ride: Book an immediate Uber ride
- schedule_ride: Schedule an Uber ride for future pickup
- get_ride_status: Get current ride status and details
- cancel_ride: Cancel an existing ride
- get_client_stats: Get usage statistics for a client
- get_usage_history: Get detailed usage history for a client
- get_ride_history: Get ride history for a client
"""

from typing import Any, Optional, Dict, List
import httpx
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("uber-central")

# Constants
UBER_CENTRAL_BASE_URL = "https://apparel-scraper--uber-central-api-serve.modal.run"
API_KEY = os.getenv("UBER_CENTRAL_API_KEY")

if not API_KEY:
    raise ValueError("UBER_CENTRAL_API_KEY environment variable is required")

# Headers for API requests
def get_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "uber-central-mcp-server/1.0.0"
    }

async def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Make a request to the Uber Central API with proper error handling."""
    url = f"{UBER_CENTRAL_BASE_URL}{endpoint}"
    headers = get_headers()
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, timeout=30.0)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data, timeout=30.0)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers, timeout=30.0)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": f"HTTP error: {str(e)}", "status_code": getattr(e.response, 'status_code', 'unknown')}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

# MCP Tools

@mcp.tool()
async def initialize_user(
    name: Optional[str] = None,
    email: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Create a new client account and return client_id for API access.
    
    Args:
        name: User's full name
        email: User's email address  
        metadata: Custom metadata (department, cost center, etc.)
    
    Returns:
        Success message with client_id or error message
    """
    request_data = {}
    if name:
        request_data["name"] = name
    if email:
        request_data["email"] = email
    if metadata:
        request_data["metadata"] = metadata
    
    result = await make_api_request("POST", "/api/v1/initialize_user", request_data)
    
    if "error" in result:
        return f"❌ Failed to initialize user: {result['error']}"
    
    client_id = result.get("client_id", "Unknown")
    message = result.get("message", "User created successfully")
    
    return f"✅ {message}\n🆔 Client ID: {client_id}\n💡 Save this client_id for all future API calls!"

@mcp.tool()
async def get_estimates(
    client_id: str,
    pickup_address: str,
    dropoff_address: str,
    capacity: int = 1
) -> str:
    """Get ride price estimates for all available vehicle types.
    
    Args:
        client_id: Valid client identifier from initialize_user
        pickup_address: Starting location (address, landmark, coordinates)
        dropoff_address: Destination location
        capacity: Number of passengers (default: 1)
    
    Returns:
        Formatted list of available ride estimates with prices and ETAs
    """
    request_data = {
        "client_id": client_id,
        "pickup_address": pickup_address,
        "dropoff_address": dropoff_address,
        "capacity": capacity
    }
    
    result = await make_api_request("POST", "/api/v1/estimates", request_data)
    
    if "error" in result:
        return f"❌ Failed to get estimates: {result['error']}"
    
    if not result or not isinstance(result, list):
        return "❌ No estimates available for this route"
    
    estimates_text = [f"🚗 Available ride estimates for {pickup_address} → {dropoff_address}:"]
    estimates_text.append("")
    
    for estimate in result:
        display_name = estimate.get("display_name", "Unknown")
        price = estimate.get("price_estimate", "Unknown")
        eta = estimate.get("estimate_time_minutes", "Unknown")
        available = "✅" if estimate.get("available", False) else "❌"
        surge = estimate.get("surge_multiplier", 1.0)
        
        surge_text = f" (🔥 {surge}x surge)" if surge > 1.0 else ""
        estimates_text.append(f"{available} {display_name}: {price} • ETA: {eta}min{surge_text}")
    
    return "\n".join(estimates_text)

@mcp.tool()
async def book_ride(
    client_id: str,
    pickup_address: str,
    dropoff_address: str,
    rider_name: str,
    rider_phone: str,
    product_id: Optional[str] = None,
    message_to_driver: Optional[str] = None,
    expense_memo: Optional[str] = None
) -> str:
    """Book an immediate Uber ride.
    
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
        Booking confirmation with ride_id and details
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
    
    result = await make_api_request("POST", "/api/v1/rides/book", request_data)
    
    if "error" in result:
        return f"❌ Failed to book ride: {result['error']}"
    
    ride_id = result.get("ride_id", "Unknown")
    status = result.get("status", "Unknown")
    message = result.get("message", "Ride booked successfully")
    
    response_text = [
        f"✅ {message}",
        f"🚗 Ride ID: {ride_id}",
        f"📍 Route: {pickup_address} → {dropoff_address}",
        f"👤 Rider: {rider_name} ({rider_phone})",
        f"📊 Status: {status}"
    ]
    
    if message_to_driver:
        response_text.append(f"💬 Driver Message: {message_to_driver}")
    
    return "\n".join(response_text)

@mcp.tool()
async def schedule_ride(
    client_id: str,
    pickup_address: str,
    dropoff_address: str,
    rider_name: str,
    rider_phone: str,
    pickup_time: str,
    product_id: Optional[str] = None,
    message_to_driver: Optional[str] = None,
    expense_memo: Optional[str] = None
) -> str:
    """Schedule an Uber ride for future pickup.
    
    Args:
        client_id: Valid client identifier
        pickup_address: Pickup location
        dropoff_address: Destination location
        rider_name: Passenger's full name
        rider_phone: Passenger's phone number
        pickup_time: Pickup time (ISO 8601 string like '2024-12-25T15:30:00')
        product_id: Specific vehicle type ID (optional)
        message_to_driver: Special instructions for driver
        expense_memo: Internal expense tracking note
        
    Returns:
        Scheduling confirmation with ride_id and details
    """
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
    
    result = await make_api_request("POST", "/api/v1/rides/schedule", request_data)
    
    if "error" in result:
        return f"❌ Failed to schedule ride: {result['error']}"
    
    ride_id = result.get("ride_id", "Unknown")
    status = result.get("status", "Unknown")
    message = result.get("message", "Ride scheduled successfully")
    
    response_text = [
        f"✅ {message}",
        f"🚗 Ride ID: {ride_id}",
        f"📍 Route: {pickup_address} → {dropoff_address}",
        f"👤 Rider: {rider_name} ({rider_phone})",
        f"🕐 Pickup Time: {pickup_time}",
        f"📊 Status: {status}"
    ]
    
    if message_to_driver:
        response_text.append(f"💬 Driver Message: {message_to_driver}")
    
    return "\n".join(response_text)

@mcp.tool()
async def get_ride_status(ride_id: str) -> str:
    """Get current ride status and details.
    
    Args:
        ride_id: Unique ride identifier from booking response
        
    Returns:
        Current ride status with driver and vehicle information
    """
    result = await make_api_request("GET", f"/api/v1/rides/{ride_id}")
    
    if "error" in result:
        return f"❌ Failed to get ride status: {result['error']}"
    
    status = result.get("status", "Unknown")
    driver_name = result.get("driver_name")
    driver_phone = result.get("driver_phone") 
    vehicle_make = result.get("vehicle_make")
    vehicle_model = result.get("vehicle_model")
    pickup_address = result.get("pickup_address", "Unknown")
    dropoff_address = result.get("dropoff_address", "Unknown")
    
    response_text = [
        f"🚗 Ride Status for {ride_id}:",
        f"📊 Status: {status}",
        f"📍 Route: {pickup_address} → {dropoff_address}"
    ]
    
    if driver_name:
        response_text.append(f"👨‍✈️ Driver: {driver_name}")
    if driver_phone:
        response_text.append(f"📞 Driver Phone: {driver_phone}")
    if vehicle_make and vehicle_model:
        response_text.append(f"🚙 Vehicle: {vehicle_make} {vehicle_model}")
    
    return "\n".join(response_text)

@mcp.tool()
async def cancel_ride(ride_id: str) -> str:
    """Cancel an existing ride.
    
    Args:
        ride_id: Unique ride identifier from booking response
        
    Returns:
        Cancellation confirmation
    """
    result = await make_api_request("DELETE", f"/api/v1/rides/{ride_id}")
    
    if "error" in result:
        return f"❌ Failed to cancel ride: {result['error']}"
    
    message = result.get("message", "Ride cancelled successfully")
    status = result.get("status", "Unknown")
    
    return f"✅ {message}\n📊 Status: {status}\n🚗 Ride ID: {ride_id}"

@mcp.tool()
async def get_client_stats(client_id: str) -> str:
    """Get usage statistics for a specific client.
    
    Args:
        client_id: Valid client identifier
        
    Returns:
        Formatted client usage statistics
    """
    result = await make_api_request("GET", f"/api/v1/users/{client_id}/stats")
    
    if "error" in result:
        return f"❌ Failed to get client stats: {result['error']}"
    
    total_calls = result.get("total_api_calls", 0)
    total_rides = result.get("total_rides", 0)
    immediate_bookings = result.get("immediate_bookings", 0)
    scheduled_rides = result.get("scheduled_rides", 0)
    cancellations = result.get("cancellations", 0)
    
    return f"""📊 Client Statistics for {client_id}:

🔧 API Usage:
  • Total API calls: {total_calls}

🚗 Ride Activity:
  • Total rides: {total_rides}
  • Immediate bookings: {immediate_bookings}
  • Scheduled rides: {scheduled_rides}
  • Cancellations: {cancellations}"""

@mcp.tool()
async def get_usage_history(client_id: str, limit: int = 10) -> str:
    """Get detailed usage history for a specific client.
    
    Args:
        client_id: Valid client identifier
        limit: Maximum records to return (default: 10, max: 100)
        
    Returns:
        Formatted usage history with API call logs
    """
    if limit > 100:
        limit = 100
        
    result = await make_api_request("GET", f"/api/v1/users/{client_id}/usage?limit={limit}")
    
    if "error" in result:
        return f"❌ Failed to get usage history: {result['error']}"
    
    usage_history = result.get("usage_history", [])
    total_records = result.get("total_records", 0)
    
    if not usage_history:
        return f"📊 No usage history found for client {client_id}"
    
    response_text = [
        f"📊 Usage History for {client_id} (showing {len(usage_history)} of {total_records} records):",
        ""
    ]
    
    for record in usage_history:
        endpoint = record.get("endpoint", "Unknown")
        timestamp = record.get("timestamp", "Unknown")
        success = "✅" if record.get("success", False) else "❌"
        exec_time = record.get("execution_time_ms", 0)
        
        response_text.append(f"{success} {endpoint} • {timestamp} • {exec_time}ms")
    
    return "\n".join(response_text)

@mcp.tool()
async def get_ride_history(client_id: str, limit: int = 10) -> str:
    """Get ride history for a specific client.
    
    Args:
        client_id: Valid client identifier
        limit: Maximum records to return (default: 10, max: 100)
        
    Returns:
        Formatted ride history with booking details
    """
    if limit > 100:
        limit = 100
        
    result = await make_api_request("GET", f"/api/v1/users/{client_id}/rides?limit={limit}")
    
    if "error" in result:
        return f"❌ Failed to get ride history: {result['error']}"
    
    ride_history = result.get("ride_history", [])
    total_records = result.get("total_records", 0)
    
    if not ride_history:
        return f"🚗 No ride history found for client {client_id}"
    
    response_text = [
        f"🚗 Ride History for {client_id} (showing {len(ride_history)} of {total_records} records):",
        ""
    ]
    
    for record in ride_history:
        ride_id = record.get("ride_id", "Unknown")
        ride_type = record.get("ride_type", "Unknown")
        timestamp = record.get("timestamp", "Unknown")
        pickup = record.get("pickup_address", "Unknown")
        dropoff = record.get("dropoff_address", "Unknown")
        status = record.get("status", "Unknown")
        
        response_text.append(f"🚗 {ride_id} • {ride_type} • {status}")
        response_text.append(f"   📍 {pickup} → {dropoff}")
        response_text.append(f"   🕐 {timestamp}")
        response_text.append("")
    
    return "\n".join(response_text)

@mcp.tool()
async def health_check() -> str:
    """Check API service health and connectivity.
    
    Returns:
        API health status information
    """
    result = await make_api_request("GET", "/")
    
    if "error" in result:
        return f"❌ API Health Check Failed: {result['error']}"
    
    service = result.get("service", "Unknown")
    version = result.get("version", "Unknown")
    status = result.get("status", "Unknown")
    endpoints = result.get("endpoints", [])
    
    response_text = [
        f"✅ {service} v{version}",
        f"📊 Status: {status}",
        f"🔧 Available endpoints: {len(endpoints)}",
        ""
    ]
    
    for endpoint in endpoints[:5]:  # Show first 5 endpoints
        response_text.append(f"  • {endpoint}")
    
    if len(endpoints) > 5:
        response_text.append(f"  ... and {len(endpoints) - 5} more")
    
    return "\n".join(response_text)

def main():
    """Main entry point for the MCP server."""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()