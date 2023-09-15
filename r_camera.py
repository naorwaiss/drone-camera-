import os
import pyrealsense2.pyrealsense2 as rs
import numpy as np
import cv2
import time

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

    try:
        start_time = time.time()
        pixel_count_sum = 0
        interval_count = 0

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
                # Count the number of pixels in the largest obstacle
                largest_obstacle_pixel_count = len(largest_obstacle)

                # Draw a bounding box around the largest obstacle
                x, y, w, h = cv2.boundingRect(largest_obstacle)
                cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Calculate the center of the largest obstacle
                center_x = x + w // 2
                center_y = y + h // 2

                # Get the depth value at the center of the obstacle
                depth_value = depth_frame.get_distance(center_x, center_y)

                # Display the distance and pixel count on the image
                distance_text = f"Depth: {depth_value:.2f} meters"
                pixel_count_text = f"Pixel Count: {largest_obstacle_pixel_count}"
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
                cv2.putText(
                    color_image,
                    pixel_count_text,
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

                # Accumulate pixel counts and increment interval count
                pixel_count_sum += largest_obstacle_pixel_count
                interval_count += 1

            # Display the color image with the largest obstacle, its distance, and pixel count
            cv2.imshow("Color Frame with Largest Obstacle", color_image)

            # Check if 3 seconds have passed
            elapsed_time = time.time() - start_time
            if elapsed_time >= 3:
                # Calculate and print the average pixel count
                if interval_count > 0:
                    average_pixel_count = pixel_count_sum / interval_count
                    print(f"Average Pixel Count: {average_pixel_count:.2f}")

                # Reset counters and timer
                start_time = time.time()
                pixel_count_sum = 0
                interval_count = 0

            key = cv2.waitKey(1)
            if key == 27:  # Press 'Esc' to exit
                break

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Stop the pipeline and close OpenCV window
        pipeline.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
