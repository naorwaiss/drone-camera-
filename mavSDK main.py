#!/usr/bin/env python3

import asyncio
from mavsdk import System
import math

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
    N = a / math.sqrt(1 - e_sq * math.sin(lat_rad)**2)
    # Calculate Cartesian coordinates
    x = (N + altitude) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (N + altitude) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (N * (1 - e_sq) + altitude) * math.sin(lat_rad)

    return x, y, z



async def get_location(drone):
    default_coordinates = (0, 0, 0)  # Provide default coordinates if telemetry data is not available

    try:
        async for position in drone.telemetry.position():
            f_latitude = position.latitude_deg
            f_longitude = position.longitude_deg
            f_altitude = position.absolute_altitude_m
            break  # Stop after obtaining coordinates once
    except Exception as e:
        print(f"Error getting location: {e}")
        print("Using default coordinates.")
        return default_coordinates

    return f_latitude, f_longitude, f_altitude

async def position_new_cartesian_coordinate(x_i, y_i, z_i, drone):
    try:
        f_latitude, f_longitude, f_altitude = await get_location(drone)
        x_n = 0
        y_n = 0
        z_n = 0
        # Calculate absolute Cartesian coordinates
        x_n, y_n, z_n = await convert_geodetic_to_cartesian(f_latitude, f_longitude, f_altitude)

        # Calculate relative Cartesian coordinates
        x_rel = x_n - x_i
        y_rel = y_n - y_i
        z_rel = z_n - z_i

        return x_rel, y_rel, z_rel
    except Exception as e:
        print(f"Error getting new position: {e}")
        return 0, 0, 0  # Return zeros if there is an error




async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return

async def run():
    #main function
    drone = System()
    await drone.connect(system_address="udp://:14540")

    status_text_task = asyncio.ensure_future(print_status_text(drone))

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    # Get initial location for relative coordinates
    first_pos = await get_location(drone)
    x_i, y_i, z_i = first_pos

    current_pos = await position_new_cartesian_coordinate(x_i, y_i, z_i, drone)
    x_new, y_new, z_new = current_pos

    print("-- Arming")
    await drone.action.arm()

    print("-- Taking off")
    target_altitude = int(input("Enter the target altitude in meters: "))
    await drone.action.set_takeoff_altitude(target_altitude)
    await drone.action.takeoff()

    await asyncio.sleep(15)

    current_pos = await position_new_cartesian_coordinate(x_i, y_i, z_i, drone)
    print("Current Position:", current_pos)

    print("-- Landing")
    await drone.action.land()

    status_text_task.cancel()

if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
