#at this function i do fusion and use converrt from geo and to geo

import asyncio
import mavsdk
from mavsdk import System
import numpy as np
from math import radians ,degrees , sqrt

# intianal value to save at the system as global




async def setup_drone(drone: System):
    """

    :param drone: the connect string to the drone
    :return: print for the user if the drone get global position it start takeoff

    *if have problem with this flag it can easely remove
    """
    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break


async def get_geo_pos(drone):

    """
    :param drone: connect strings
    :return: the current position of the drone at geo
    """
    default_coordinates = (0, 0, 0)
    try:
        async for position in drone.telemetry.position():
            latitude = position.latitude_deg
            longitude = position.longitude_deg
            altitude = position.absolute_altitude_m
            break
    except Exception as e:
        print(f"Error getting location: {e}")
        print("Using default coordinates.")
        return default_coordinates

    return latitude, longitude, altitude


async def geodetic_to_cartesian_ned(drone):

    """
    :param drone: connect string
    :return: make geo position to cartazian one and rotate it to right hand axis ned coordinate
    """
    latitude,longitude,altitude = await get_geo_pos(drone)
    # Constants for Earth (assuming it's a perfect sphere)
    radius_earth = 6371000.0  # in meters

    # Convert latitude and longitude from degrees to radians
    lat_rad = radians(latitude)
    lon_rad = radians(longitude)

    # Convert reference latitude and longitude from degrees to radians
    ref_lat_rad = radians(latitude_i)
    ref_lon_rad = radians(longitude_i)

    # Calculate the difference in coordinates
    delta_lat = lat_rad - ref_lat_rad
    delta_lon = lon_rad - ref_lon_rad
    delta_altitude = altitude - altitude_i

    # Convert geodetic coordinates to Cartesian coordinates (NED convention)
    ned_x = radius_earth * delta_lat
    ned_y = radius_earth * delta_lon
    ned_z = delta_altitude  # Negate altitude to align with NED convention

    rotation_matrix = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
    ned_coordinates = np.dot(rotation_matrix, np.array([ned_x, ned_y, ned_z]))
    x_final ,y_final,z_final =ned_coordinates

    print(f"At cartzian position: x_i={x_final}, y_i={y_final}, z_i={z_final} meters")
    return x_final,y_final,z_final



async def cartesian_to_geodetic(x, y, z, drone):
    # the revers function - from cartazian go to geo
    # Constants for Earth (assuming it's a perfect sphere)
    radius_earth = 6371000.0  # in meters

    # Define the rotation matrix for the reverse transformation
    rotation_matrix = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])

    # Apply the reverse rotation to get NED coordinates
    ned_coordinates = np.dot(rotation_matrix, np.array([x, y, z]))

    # Extract NED coordinates
    ned_x, ned_y, ned_z = ned_coordinates

    # Get reference geodetic coordinates
    ref_latitude, ref_longitude, ref_altitude = await get_geo_pos(drone)
    ref_lat_rad = radians(ref_latitude)
    ref_lon_rad = radians(ref_longitude)

    # Convert NED coordinates to geodetic coordinates
    delta_lat = ned_x / radius_earth
    delta_lon = ned_y / radius_earth
    delta_altitude = ned_z

    lat_rad = ref_lat_rad + delta_lat
    lon_rad = ref_lon_rad + delta_lon
    altitude = ref_altitude + delta_altitude

    # Convert back to degrees
    latitude = degrees(lat_rad)
    longitude = degrees(lon_rad)


    return latitude, longitude, altitude

async def takeoff_presedoure(drone,target_altitude):

    """
    :param drone: the connect strings
    :return: takeoff the drone
    """

    #  need to add change to stabilize mode

    await drone.action.set_takeoff_altitude(target_altitude)
    await asyncio.sleep(1)
    print("-- Arming")
    await drone.action.arm()
    await drone.action.takeoff()
    await asyncio.sleep(15)  # need to change to the spare function
    await geodetic_to_cartesian_ned(drone)
    return



async def absolute_yaw(drone):
    async for attitude_info in drone.telemetry.attitude_euler():
        absolute_yaw = attitude_info.yaw_deg
        return absolute_yaw





async def x_axes(x_dist, drone):
    # get local position
    x_local, y_local, z_local = await geodetic_to_cartesian_ned(drone)
    lat_dist, long_dist, alt_dist = await cartesian_to_geodetic(x_dist, y_local, z_local, drone)

    # Remove the yaw check
    yaw = await absolute_yaw(drone)
    await drone.action.goto_location(lat_dist, long_dist, alt_dist, yaw)
    print(await geodetic_to_cartesian_ned(drone))

    return



async def y_axes(drone):

    return





async def main():
    global latitude_i, longitude_i, altitude_i
    x_initial = y_initial = z_initial = latitude_i = longitude_i = altitude_i = 0


    drone = System()
    await drone.connect(system_address="udp://:14540")
    #await drone.connect(system_address="serial:///dev/ttyTHS1")
    await setup_drone(drone)


    #get first coordinate with geo
    latitude_i,longitude_i,altitude_i=await get_geo_pos(drone)
    print(f"At GPS position: Latitude={latitude_i}, Longitude={longitude_i}, Altitude={altitude_i} meters")
    x_initial,y_initial,z_initial=await  geodetic_to_cartesian_ned(drone)


        # at this section need add
        # 1) validation that the drone is at offbord mode

    target_altitude = int(input("Enter the target altitude in meters: "))
    await takeoff_presedoure(drone,target_altitude)

    #at this point the go to loop is start

    await x_axes(15,drone)




    await drone.action.land()




if __name__ == "__main__":
    asyncio.run(main())

