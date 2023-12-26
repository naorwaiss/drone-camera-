import asyncio
from mavsdk import System
import numpy as np
from math import cos, sin, radians

def geodetic_to_cartesian_ned(longitude, latitude, altitude, ref_longitude, ref_latitude, ref_altitude):
    # Constants for Earth (assuming it's a perfect sphere)
    radius_earth = 6371000.0  # in meters

    # Convert latitude and longitude from degrees to radians
    lat_rad = radians(latitude)
    lon_rad = radians(longitude)

    # Convert reference latitude and longitude from degrees to radians
    ref_lat_rad = radians(ref_latitude)
    ref_lon_rad = radians(ref_longitude)

    # Calculate the difference in coordinates
    delta_lat = lat_rad - ref_lat_rad
    delta_lon = lon_rad - ref_lon_rad
    delta_altitude = altitude - ref_altitude

    # Convert geodetic coordinates to Cartesian coordinates (NED convention)
    ned_x = -radius_earth * delta_lat  # Negate x-coordinate to have positive forward
    ned_y = radius_earth * delta_lon
    ned_z = delta_altitude  # Negate altitude to align with NED convention

    # Rotate coordinates to right-handed system
    rotation_matrix = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    ned_coordinates = np.dot(rotation_matrix, np.array([ned_x, ned_y, ned_z]))

    return ned_coordinates


async def position_task(drone):
    # Set initial reference point
    ref_longitude, ref_latitude, ref_altitude = 0, 0, 0

    async for position in drone.telemetry.position():
        if ref_longitude == 0 and ref_latitude == 0 and ref_altitude == 0:
            ref_longitude = position.longitude_deg
            ref_latitude = position.latitude_deg
            ref_altitude = position.relative_altitude_m
            break  # Only need the first position

    async for position in drone.telemetry.position():
        longitude = position.longitude_deg
        latitude = position.latitude_deg
        altitude = position.relative_altitude_m

        ned_coordinates = geodetic_to_cartesian_ned(
            longitude, latitude, altitude, ref_longitude, ref_latitude, ref_altitude)

        print("Latitude: {:.6f}, Longitude: {:.6f}, Altitude: {:.2f}".format(latitude, longitude, altitude))
        print("NED Coordinates:", ned_coordinates)

async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")

    await asyncio.gather(position_task(drone))

if __name__ == "__main__":
    asyncio.run(main())
