import os
import pyrealsense2.pyrealsense2 as rs
import numpy as np
import cv2
import math

# Set an environment variable to disable GUI
os.environ["DISPLAY"] = ":0.0"

def main():
    # Create a context
    pipeline = rs.pipeline()
    config = rs.config()

    # Enable both depth and color streams with the desired settings
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

    # Start the pipeline
    pipeline.start(config)

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Change the codec to 'MJPG'
    output_file = '/home/drone/Desktop/output.avi'
    fps = 30  # Frames per second
    frame_size = (640, 480)  # Match the frame size to your input stream

    out = cv2.VideoWriter(output_file, fourcc, fps, frame_size)

    # Calculate the center of the camera's image
    camera_center_x = frame_size[0] // 2
    camera_center_y = frame_size[1] // 2

    # Camera parameters (based on your provided FOV values)
    fov_x_degrees_rgb = 70.0  # Horizontal field of view for RGB sensor in degrees
    fov_y_degrees_rgb = 43.0  # Vertical field of view for RGB sensor in degrees

    try:
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = None
            for _ in range(5):
                frames = pipeline.wait_for_frames(timeout_ms=2000)  # Wait for up to 1 second
                if frames:
                    break

            if frames is None:
                print("No frames received within the timeout.")
                continue

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                continue

            # Get the color image as a numpy array
            color_image = np.asanyarray(color_frame.get_data())

            # Convert the color image to HSV
            hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

            # Define lower and upper bounds for the red color (adjust as needed)
            lower_red1 = np.array([0, 100, 100])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([160, 100, 100])
            upper_red2 = np.array([180, 255, 255])

            # Create masks for both ranges of red
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

            # Combine both masks to detect strong red colors
            mask = cv2.bitwise_or(mask1, mask2)

            # Apply morphological operations to the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)

            # Find contours in the mask
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Initialize variables to keep track of the largest obstacle
            largest_area = 0
            largest_obstacle = None

            for contour in contours:
                # Calculate the area of the contour
                area = cv2.contourArea(contour)

                # Find the largest obstacle
                if area > largest_area:
                    largest_area = area
                    largest_obstacle = contour

            if largest_obstacle is not None:
                # Calculate the center of the largest obstacle
                x, y, w, h = cv2.boundingRect(largest_obstacle)

                # Draw a bounding box around the largest obstacle (green color)
                cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calculate the center of the largest obstacle
                contour_center_x = x + w // 2
                contour_center_y = y + h // 2

                # Initialize right and up vectors
                right_rgb = 1  # Default value
                up_rgb = 1  # Default value

                # Get the depth value at the center of the obstacle (in millimeters)
                depth_value = depth_frame.get_distance(contour_center_x, contour_center_y) * 1000

                if depth_value > 0:  # Check if valid depth value
                    # Calculate the right and up vectors for RGB sensor (in meters) based on the pixel coordinates
                    # Use the depth value in millimeters for accurate calculations
                    vector_x_rgb = contour_center_x - camera_center_x
                    vector_y_rgb = contour_center_y - camera_center_y
                    right_rgb = vector_x_rgb * math.tan(math.radians(fov_x_degrees_rgb / 2)) * (depth_value / frame_size[0])
                    up_rgb = vector_y_rgb * math.tan(math.radians(fov_y_degrees_rgb / 2)) * (depth_value / frame_size[1])

                # Display the vector and depth information on the image
                cv2.arrowedLine(
                    color_image,
                    (camera_center_x, camera_center_y),
                    (contour_center_x, contour_center_y),
                    (0, 0, 255), 2  # Red color for the vector
                )

                distance_text = f"Depth: {depth_value:.2f} mm\nRight (RGB): {right_rgb:.2f} meters\nUp (RGB): {up_rgb:.2f} meters"
                cv2.putText(
                    color_image,
                    distance_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

            # Display the color image with the largest obstacle, its distance, and the vector
            cv2.imshow("Color Frame with Largest Obstacle", color_image)
            # Write the frame to the output video
            out.write(color_image)

            key = cv2.waitKey(1)
            if key == 27:  # Press 'Esc' to exit
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Stop the pipeline and close OpenCV window
        pipeline.stop()
        out.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
