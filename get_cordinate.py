import asyncio
from mavsdk import System
import math


async def get_home_position(drone):
    async for home in drone.telemetry.home():
        home_latitude_deg = home.latitude_deg
        home_longitude_deg = home.longitude_deg
        home_altitude_m = home.relative_altitude_m
        return home_latitude_deg, home_longitude_deg, home_altitude_m


async def get_drone_position_and_convert():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    home_latitude_deg, home_longitude_deg, home_altitude_m = await get_home_position(drone)

    initial_altitude_m = None  # Store the initial altitude

    async for position in drone.telemetry.position():
        if initial_altitude_m is None:
            initial_altitude_m = position.absolute_altitude_m  # Capture initial altitude

        # Calculate Cartesian coordinates with respect to the home position
        x = (position.longitude_deg - home_longitude_deg) * 111319.9 * math.cos(math.radians(position.latitude_deg))
        y = (position.latitude_deg - home_latitude_deg) * 111319.9
        z = position.absolute_altitude_m - initial_altitude_m  # Adjust for initial altitude
        z = position.absolute_altitude_m - initial_altitude_m  # Adjust for initial altitude

        print(f"Cartesian Coordinates: x={x}, y={y}, z={z}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_drone_position_and_convert())
