"""
Example usage of ServiceManager with AbstractService implementations.

This file demonstrates how to use the ServiceManager to get service instances
using the Factory and Singleton patterns.
"""

# Example 1: Using ServiceManager directly
from helpers.service_manager import ServiceManager
from auth.services.auth_service import AuthService
from marketdata.services.market_data_service import MarketDataService

# Get the singleton ServiceManager instance
service_manager = ServiceManager()

# Get service instances (creates them if they don't exist)
auth_service = service_manager.get_service(AuthService)
market_service = service_manager.get_service(MarketDataService)

# Getting the same service again returns the same instance
auth_service_2 = service_manager.get_service(AuthService)
assert auth_service is auth_service_2  # Same instance

print(f"AuthService instance: {id(auth_service)}")
print(f"AuthService instance 2: {id(auth_service_2)}")
print(f"Are they the same? {auth_service is auth_service_2}")


# Example 2: Using convenience functions
from helpers.service_manager import get_service, has_service

# Get services using convenience function
auth_service_conv = get_service(AuthService)
market_service_conv = get_service(MarketDataService)

# Check if services exist
print(f"AuthService exists: {has_service(AuthService)}")
print(f"MarketDataService exists: {has_service(MarketDataService)}")

# These are the same instances as before (Singleton pattern)
assert auth_service is auth_service_conv
assert market_service is market_service_conv


# Example 3: Service information
print("Registered services:")
for name, instance_str in service_manager.get_registered_services().items():
    print(f"  - {name}: {instance_str}")

print(f"Total services: {service_manager.get_service_count()}")


# Example 4: Using services (they work exactly as before)
try:
    # Example auth service usage
    auth_service.validate_login_data("testuser", "password123")
    print("✅ Auth service validation passed")

    # Example market data service usage
    exchanges = market_service.get_available_exchanges(limit=5)
    print(f"✅ Market service returned {len(exchanges)} exchanges")

except Exception as e:
    print(f"❌ Service error: {e}")


# Example 5: Error handling - trying to register invalid service
try:
    class InvalidService:
        """This class doesn't extend AbstractService"""
        pass

    service_manager.get_service(InvalidService)  # This will raise TypeError
except TypeError as e:
    print(f"✅ Correctly caught error: {e}")


print("\n🎉 ServiceManager examples completed successfully!")
