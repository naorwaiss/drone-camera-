import asyncio
from mavsdk import System
from mavsdk.mission import MissionItem
from mavsdk.offboard import PositionNedYaw, OffboardError
import time

# Function to convert GPS coordinates to Cartesian coordinates
import math


def convert_gps_to_cartesian(latitude_deg, longitude_deg, altitude_m, home_latitude_deg, home_longitude_deg,
                             home_altitude_m):
    # Earth radius in meters
    earth_radius = 6371000.0

    # Convert latitude and longitude to radians
    lat_rad = math.radians(latitude_deg)
    lon_rad = math.radians(longitude_deg)
    home_lat_rad = math.radians(home_latitude_deg)
    home_lon_rad = math.radians(home_longitude_deg)

    # Calculate Cartesian coordinates relative to the home location
    x = earth_radius * (lon_rad - home_lon_rad) * math.cos(home_lat_rad)
    y = earth_radius * (lat_rad - home_lat_rad)
    z = altitude_m - home_altitude_m

    return x, y, z


async def arm_and_takeoff(drone, altitude):
    await drone.action.set_takeoff_altitude(altitude)
    await move(drone, 0.0, 0.0, -altitude)
    await drone.action.arm()
    await asyncio.sleep(1)
    await drone.action.setup_drone()
    print("Drone is armed and taking off...")


async def move(drone, target_north_m, target_east_m, target_down_m):
    try:
        new_position = PositionNedYaw(target_north_m, target_east_m, target_down_m, 0.0)
        await drone.offboard.set_position_ned(new_position)
        await asyncio.sleep(1)
    except Exception as e:
        print(f"Failed moving {e}")


async def land(drone):
    try:
        await drone.action.land()
        print("Drone is landing...")
    except Exception as e:
        print(f"Error landing: {e}")


async def telemetry_loop(drone):
    async for current_position in drone.telemetry.position_velocity_ned():
        try:
            position = current_position.position
            yield position.north_m, position.east_m, position.down_m
        except Exception as e:
            print(f"Error in telemetry loop: {e}")


async def main():
    # Your main control logic here
    altitude = float(input("Enter desired altitude (in meters): "))

    drone = System()

    try:
        await drone.connect(system_address="udp://:14540")

        await asyncio.sleep(10)  # Allow time for takeoff

        print(">> Waiting for GPS")
        async for state in drone.telemetry.health():
            if state.is_global_position_ok:
                break
        print(">> Found GPS")

        async for north_m, east_m, down_m in telemetry_loop(drone):
            distance_calculator = {
                "north": lambda target_distance: (
                    north_m + target_distance, east_m, down_m),
                "east": lambda target_distance: (
                    north_m, east_m + target_distance, down_m),
                "up": lambda target_distance: (
                    north_m, east_m, down_m + target_distance),
            }
            command = input(f"Enter direction to move {list(distance_calculator.keys())} or 'land' to land: ")
            if command == "land":
                await land(drone)
                await asyncio.sleep(5)  # Allow time for movement
                break
            else:
                distance = float(input("Enter distance to move (in meters): "))
                target_north_m, target_east_m, target_down_m = distance_calculator[command](
                    distance)
                print(
                    f"Moving from ({north_m}, {east_m}, {down_m}) -> ({target_north_m}, {target_east_m}, {target_down_m})")
                await move(drone, target_north_m, target_east_m, target_down_m)
                await asyncio.sleep(5)  # Allow time for movement
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
