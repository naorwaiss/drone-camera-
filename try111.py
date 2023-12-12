import asyncio
from mavsdk import System
import math

async def convert_geodetic_to_cartesian(latitude, longitude, altitude):
    # Constants
    a = 6378137.0  # Semi-major axis of the Earth in meters
    f = 1 / 298.257223563  # Flattening
    e_sq = f * (2 - f)  # Eccentricity squared

    # Convert latitude and longitude to radians
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)

    # Calculate N value
    N = a / math.sqrt(1 - e_sq * math.sin(lat_rad) ** 2)

    # Calculate Cartesian coordinates
    x = (N + altitude) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (N + altitude) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (N * (1 - e_sq) + altitude) * math.sin(lat_rad)

    return x, y, z

async def print_gps_and_cartesian_position():
    drone = System()

    await drone.connect(system_address="udp://:14540")

    try:
        while True:
            gps_info = await drone.telemetry.position()
            latitude = gps_info.latitude_deg
            longitude = gps_info.longitude_deg
            altitude = gps_info.absolute_altitude_m

            cartesian_coordinates = await convert_geodetic_to_cartesian(latitude, longitude, altitude)

            print(f"GPS Position: Lat={latitude}, Lon={longitude}, Alt={altitude} meters")
            print(f"Cartesian Coordinates: X={cartesian_coordinates[0]}, Y={cartesian_coordinates[1]}, Z={cartesian_coordinates[2]}")

            await asyncio.sleep(1)  # Adjust the sleep time as needed
    except KeyboardInterrupt:
        pass  # Allow user to interrupt the loop with Ctrl+C

    await drone.disconnect()

if __name__ == "__main__":
    asyncio.run(print_gps_and_cartesian_position())
