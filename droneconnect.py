from dronekit import connect, VehicleMode
import time

# Connect to the drone
#connection_string= "tcp:127.0.0.1:5760"
connection_string = "/dev/ttyTHS1"
baud_rate = 57600  # Corrected baud rate
vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)


def check_armable_and_arm():
    print("Connecting to the vehicle...")
    while not vehicle.is_armable:
        print("Waiting for GPS and armability...")
        time.sleep(1)

    print("Vehicle is armable")

    # Arming the vehicle
    print("Arming the vehicle...")
    vehicle.armed = True
    while not vehicle.armed:
        print("Waiting for the vehicle to arm...")
        time.sleep(1)

    print("Vehicle is armed")


def print_location_info():
    # Print current location latitude, longitude, and altitude
    current_location = vehicle.location.global_relative_frame
    print(
        "Current Location: Lat=%s, Lon=%s, Alt=%s" % (current_location.lat, current_location.lon, current_location.alt))

    # Print home location latitude, longitude, and altitude
    home_location = vehicle.home_location
    print("Home Location: Lat=%s, Lon=%s, Alt=%s" % (home_location.lat, home_location.lon, home_location.alt))


def arm_and_takeoff(target_altitude):
    print_location_info()

    print("Taking off to %s meters..." % target_altitude)
    vehicle.simple_takeoff(target_altitude)

    while True:
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude of %s meters" % target_altitude)
            break
        time.sleep(1)


def main():
    check_armable_and_arm()

    target_altitude = 3  # Desired target altitude in meters
    arm_and_takeoff(target_altitude)

    # The rest of your code here
    # ... other code ...


if __name__ == "__main__":
    main()
