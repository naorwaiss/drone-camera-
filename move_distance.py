# this simulation is only move the drone and gave him command this code also reset the position of the drone to new orgin)

import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)

MOVE_ACCURACY = 0.1


async def setup_drone(drone: System):
    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.set_takeoff_altitude(2.5)
    await drone.action.arm()
    await drone.action.takeoff()
    print("take off to defult altitude of 2.5")
    await asyncio.sleep(15)

    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.5, 0.0))
    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed \
                with error code: {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        raise


async def land(drone: System):
    await move(drone, 0.0, 0.0, 0.0)
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed \
                with error code: {error._result.result}")
    await drone.action.land()


async def move(drone: System, north_m: float, east_m: float, down_m: float, yaw_deg: float = 0.0):
    await drone.offboard.set_position_ned(
        PositionNedYaw(north_m, east_m, down_m, yaw_deg))
    while True:
        await asyncio.sleep(0.1)
        position_ned = await drone.telemetry.position_velocity_ned().__aiter__().__anext__()
        north_m_distance = position_ned.position.north_m - north_m
        east_m_distance = position_ned.position.east_m - east_m
        down_m_distance = position_ned.position.down_m - down_m
        if (
                MOVE_ACCURACY > north_m_distance > -MOVE_ACCURACY
                and MOVE_ACCURACY > east_m_distance > -MOVE_ACCURACY
                and MOVE_ACCURACY > down_m_distance > -MOVE_ACCURACY
        ):
            break


async def move_loop(drone: System):
    position_ned = await drone.telemetry.position_velocity_ned().__aiter__().__anext__()
    position = position_ned.position
    print(f">> Current position ({position.north_m}, {-position.east_m}, {-position.down_m})")
    direction = input("Enter direction [forward, right, up, land]: ")
    if direction == "land":
        await land(drone)
    else:
        distance = float(input("Enter distance [in meters]: "))
        target_north_m = position.north_m
        target_east_m = position.east_m
        target_down_m = position.down_m
        if direction == "forward":
            target_north_m += distance
        elif direction == "right":
            target_east_m += distance
        elif direction == "up":
            target_down_m -= distance
        await move(drone, target_north_m, target_east_m, target_down_m)


async def main():
    drone = System()
    await drone.connect(system_address="udp://:14540")
    #await drone.connect(system_address="serial:///dev/ttyTHS1")
    await setup_drone(drone)

    height = float(input(
        "Enter drone height [in meters]: "
    ))

    async for position_ned in drone.telemetry.position_velocity_ned():
        position = position_ned.position
        await move(drone, position.north_m, position.east_m, -height)
        break

    while True:
        try:
            await move_loop(drone)
        except Exception as e:
            print(f">> Failed with {e}, landing")
            await land(drone)


if __name__ == "__main__":
    asyncio.run(main())
