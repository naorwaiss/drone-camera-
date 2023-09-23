import asyncio
from mavsdk import System
from mavsdk.offboard import PositionNedYaw
from convert_coordinates import convert_gps_to_cartesian
import time


async def arm_and_takeoff(drone, altitude):
    await drone.action.set_takeoff_altitude(altitude)
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -altitude, 0.0))
    await drone.offboard.start()
    await asyncio.sleep(1)
    await drone.action.arm()
    await asyncio.sleep(1)
    await drone.action.takeoff()
    print("Drone is armed and taking off...")


async def move_forward(drone, distance):
    try:
        current_position = await drone.telemetry.position()
        x, y, z = convert_gps_to_cartesian(
            current_position.latitude_deg,
            current_position.longitude_deg,
            current_position.absolute_altitude_m,
            home_latitude_deg,
            home_longitude_deg,
            home_altitude_m
        )

        target_x = x + distance
        await drone.offboard.set_position_ned(PositionNedYaw(0.0, distance, -z, 0.0))
        print(f"Moving forward by {distance} meters...")
    except Exception as e:
        print(f"Error moving forward: {e}")


async def land(drone):
    try:
        await drone.action.land()
        print("Drone is landing...")
    except Exception as e:
        print(f"Error landing: {e}")


async def telemetry_loop(drone):
    while True:
        try:
            current_position = await drone.telemetry.position()
            x, y, z = convert_gps_to_cartesian(
                current_position.latitude_deg,
                current_position.longitude_deg,
                current_position.absolute_altitude_m,
                home_latitude_deg,
                home_longitude_deg,
                home_altitude_m
            )
            print(f"Current Coordinates: X={x}, Y={y}, Z={z}")
            await asyncio.sleep(1)  # Sleep for 1 second
        except Exception as e:
            print(f"Error in telemetry loop: {e}")


async def main():
    altitude = float(input("Enter desired altitude (in meters): "))

    drone = System()

    try:
        await drone.connect(system_address="udp://:14540")

        await arm_and_takeoff(drone, altitude)

        asyncio.create_task(telemetry_loop(drone))  # Start telemetry loop concurrently

        await asyncio.sleep(5)  # Allow time for takeoff

        distance = float(input("Enter distance to move forward (in meters): "))

        await move_forward(drone, distance)
        await asyncio.sleep(5)  # Allow time for movement

        land_confirmation = input("Enter 'land' to initiate landing: ")
        if land_confirmation.lower() == 'land':
            await land(drone)
        else:
            print("Landing aborted.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Replace these values with the actual home location of your drone
    home_latitude_deg = 0.0
    home_longitude_deg = 0.0
    home_altitude_m = 0.0

    asyncio.run(main())
