import asyncio
from mavsdk import System
import math

global x_initial, y_initial, z_initial, latitude_i, longitude_i, altitude_i
x_initial = y_initial = z_initial = latitude_i = longitude_i = altitude_i = 0


async def get_location(drone):
    global latitude_i, longitude_i, altitude_i

    default_coordinates = (0, 0, 0)

    try:
        async for position in drone.telemetry.position():
            latitude_i = position.latitude_deg
            longitude_i = position.longitude_deg
            altitude_i = position.absolute_altitude_m
            break
    except Exception as e:
        print(f"Error getting location: {e}")
        print("Using default coordinates.")
        return default_coordinates

    return latitude_i, longitude_i, altitude_i


async def convert_geodetic_to_cartesian(latitude, longitude, altitude):
    # Constants
    radius_earth = 6371.0

    # Convert latitude and longitude from degrees to radians
    latitude_rad = math.radians(latitude)
    longitude_rad = math.radians(longitude)

    # Calculate Cartesian coordinates
    x = (radius_earth + altitude) * math.cos(latitude_rad) * math.cos(longitude_rad)
    y = (radius_earth + altitude) * math.cos(latitude_rad) * math.sin(longitude_rad)
    z = (radius_earth + altitude) * math.sin(latitude_rad)

    return x, y, z


async def position_new_cartzian(drone):
    global x_initial, y_initial, z_initial, latitude_i, longitude_i, altitude_i

    latitude, longitude, altitude = 0, 0, 0
    try:
        latitude, longitude, altitude = await get_location(drone)
        x_n, y_n, z_n = await convert_geodetic_to_cartesian(latitude, longitude, altitude)

        x_rel = (x_n - x_initial)
        y_rel = (y_n - y_initial)
        z_rel = (z_n - z_initial)

        return x_rel, y_rel, z_rel
    except Exception as e:
        print(f"Error getting new position: {e}")
    return 0, 0, 0


async def print_status_text(drone):
    try:
        async for status_text in drone.telemetry.status_text():
            print(f"Status: {status_text.type}: {status_text.text}")
    except asyncio.CancelledError:
        return


async def run():
    global x_initial, y_initial, z_initial, latitude_i, longitude_i, altitude_i

    drone = System()
    await drone.connect(system_address="udp://:14540")

    status_text_task = asyncio.ensure_future(print_status_text(drone))

    try:
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

        latitude_i, longitude_i, altitude_i = await get_location(drone)
        print(f"At GPS position: Latitude={latitude_i}, Longitude={longitude_i}, Altitude={altitude_i} meters")
        x_initial, y_initial, z_initial = await convert_geodetic_to_cartesian(latitude_i, longitude_i, altitude_i)
        print(f"At Cartesian position: x={x_initial}, y={y_initial}, z={z_initial}")
        print(await position_new_cartzian(drone))

        print("-- Arming")
        await drone.action.arm()

        print("-- Taking off")
        target_altitude = int(input("Enter the target altitude in meters: "))
        await drone.action.set_takeoff_altitude(target_altitude)
        await drone.action.takeoff()

        await asyncio.sleep(15)
        print(await get_location(drone))
        print(await position_new_cartzian(drone))
        print("-- Landing")
        await drone.action.land()

    finally:
        # Properly cancel and await completion of status_text_task
        status_text_task.cancel()
        await asyncio.gather(status_text_task, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(run())