from dronekit import connect, VehicleMode
import time
from home_origin_script import calculate_correct_location, home_origin


# Connect to the simulator running on the local machine
connection_string = "tcp:127.0.0.1:5760"
vehicle = connect(connection_string, wait_ready=True)

def arm_and_takeoff(target_altitude):
    print("Arming motors")
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("Taking off to {} meters".format(target_altitude))
    vehicle.simple_takeoff(target_altitude)

    while True:
        current_altitude = vehicle.location.global_relative_frame.alt
        if current_altitude >= target_altitude * 0.95:
            print("Target altitude reached")
            break
        time.sleep(1)

def land():
    print("Initiating landing...")
    vehicle.mode = VehicleMode("LAND")

    while vehicle.armed:
        print("Waiting for landing...")
        time.sleep(1)

    print("Landed")

def main():
    target_altitude = 10  # Desired altitude in meters
    arm_and_takeoff(target_altitude)

    home_origin(vehicle)

    # Wait for 10 seconds after reaching target altitude
    print("Waiting for 10 seconds...")
    time.sleep(10)

    # Print the x, y values (distance from the origin)
    home_location, current_location = home_origin(vehicle)
    x_distance, y_distance = calculate_correct_location(home_location, current_location)
    print("Current location (x,y): {}m, {}m".format(x_distance, y_distance))

    # Initiate landing process
    land()

if __name__ == "__main__":
    main()
