#!/usr/bin/env python3"""Caveat when attempting to run the examples in non-gps environments:`drone.offboard.stop()` will return a `COMMAND_DENIED` result because itrequires a mode switch to HOLD, something that is currently not supported in anon-gps environment."""import asynciofrom coordinate import get_geo_pos,geodetic_to_cartesian_nedfrom mavsdk import System,telemetryfrom mavsdk.offboard import (OffboardError, PositionNedYaw)async def absolute_yaw(drone):    async for attitude_info in drone.telemetry.attitude_euler():        absolute_yaw = attitude_info.yaw_deg        return absolute_yawasync def prepare_offboard(drone):    """    :param drone:    the connect string    :return:    the drone change to offboard     """    print("Waiting for drone to connect...")    async for state in drone.core.connection_state():        if state.is_connected:            print(f"-- Connected to drone!")            break    print("Waiting for drone to have a global position estimate...")    async for health in drone.telemetry.health():        if health.is_global_position_ok and health.is_home_position_ok:            print("-- Global position estimate OK")            break    print("-- Setting initial setpoint")    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0))    print("-- Starting offboard")    try:        await drone.offboard.start()    except OffboardError as error:        print(f"Starting offboard mode failed \                   with error code: {error._result.result}")        print("-- Disarming")        await drone.action.disarm()        return    returnasync def run():    """ Does Offboard control using position NED coordinates. """    global latitude_i, longitude_i, altitude_i    latitude_i = longitude_i = altitude_i = 0    drone = System()    await drone.connect(system_address="udp://:14540")    latitude_i, longitude_i, altitude_i = await get_geo_pos(drone)    await prepare_offboard(drone)    # take off to offboard mode    yaw_i = await absolute_yaw(drone)    target_altitude = int(input("Enter the target altitude in meters: "))    print("-- Arming")    await drone.action.arm()    print ("takeoff")    await drone.offboard.set_position_ned(            PositionNedYaw(0.0, 0.0, -target_altitude, yaw_i))    await asyncio.sleep(10)    print("change to nose of the drone to the north")    await drone.offboard.set_position_ned(        PositionNedYaw(0.0, 0.0, -target_altitude, 0))    await asyncio.sleep(2)    print (await geodetic_to_cartesian_ned(drone,latitude_i, longitude_i, altitude_i))    await drone.action.land()    await asyncio.sleep(15)    print("-- Stopping offboard")    try:        await drone.offboard.stop()    except OffboardError as error:        print(f"Stopping offboard mode failed \                with error code: {error._result.result}")if __name__ == "__main__":    # Run the asyncio loop    asyncio.run(run())