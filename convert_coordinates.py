import math

def convert_gps_to_cartesian(latitude_deg, longitude_deg, altitude_m, home_latitude_deg, home_longitude_deg, home_altitude_m):
    # Earth radius in meters
    earth_radius = 6371000.0

    # Convert latitude and longitude to radians
    lat_rad = math.radians(latitude_deg)
    lon_rad = math.radians(longitude_deg)
    home_lat_rad = math.radians(home_latitude_deg)
    home_lon_rad = math.radians(home_longitude_deg)

    # Calculate Cartesian coordinates
    x = earth_radius * (lon_rad - home_lon_rad) * math.cos(lat_rad)
    y = earth_radius * (lat_rad - home_lat_rad)
    z = altitude_m - home_altitude_m

    return x, y, z

if __name__ == "__main__":
    # Replace these values with the actual home location of your drone
    home_latitude_deg = 0.0
    home_longitude_deg = 0.0
    home_altitude_m = 0.0

    # Replace these values with the GPS coordinates obtained from Script 1
    latitude_deg = 41.0
    longitude_deg = -74.0
    altitude_m = 100.0

    x, y, z = convert_gps_to_cartesian(latitude_deg, longitude_deg, altitude_m, home_latitude_deg, home_longitude_deg, home_altitude_m)
    print(f"Cartesian Coordinates: x={x}, y={y}, z={z}")
