def calculate_correct_location(home_location, current_location):
    if home_location is None or current_location is None:
        return None, None

    # Calculate differences in latitude and longitude
    delta_lat = current_location.lat - home_location.lat
    delta_lon = current_location.lon - home_location.lon

    # Convert differences to meters (assuming 1 degree of latitude/longitude is approximately 111,000 meters)
    x_distance = delta_lat * 111000
    y_distance = delta_lon * 111000

    return x_distance, y_distance

def home_origin(vehicle):
    home_location = vehicle.home_location
    current_location = vehicle.location.global_relative_frame

    if home_location is None or current_location is None:
        print("Failed to retrieve location data.")
        return

    x_distance, y_distance = calculate_correct_location(home_location, current_location)

    print("Home position: Latitude={}, Longitude={}, Altitude={}".format(
        home_location.lat, home_location.lon, home_location.alt))

    print("Correct location (x,y): {}m, {}m".format(x_distance, y_distance))
