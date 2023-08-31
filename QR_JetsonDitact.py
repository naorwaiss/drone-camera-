import cv2
import numpy as np
import os
import pyrealsense2.pyrealsense2 as rs
from pyzbar.pyzbar import decode

# Set an environment variable to disable GUI
os.environ["DISPLAY"] = ":0.0"

# Initialize the Intel RealSense pipeline
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

# Start the pipeline
pipeline.start(config)

# Initialize dist_QR to None
dist_QR = None

while True:
    # Wait for the next set of frames from the Intel RealSense camera
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()
    color_frame = frames.get_color_frame()

    # Convert the color frame to a numpy array
    frame = np.asanyarray(color_frame.get_data())

    # Decode QR codes in the frame
    decoded_objects = decode(frame)

    # Process detected QR codes
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')

        # Check if the QR code data is 'drone'
        if data == 'drone':
            # Get the QR code's four corners
            points = obj.polygon

            # Convert points to numpy array for contour drawing
            points = np.array(points, dtype=np.int32)

            # Draw a green contour around the 'drone' QR code
            cv2.polylines(frame, [points], isClosed=True, color=(0, 255, 0), thickness=2)

            # Calculate the center of the contour
            cx, cy = np.mean(points, axis=0).astype(int)

            # Draw a red point at the center of the contour
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            # Calculate the distance to the QR code
            dist_QR = depth_frame.get_distance(cx, cy)

            # Display the QR code data and distance
            cv2.putText(frame, f"Data: {data}", (obj.rect.left, obj.rect.top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, f"Distance: {dist_QR:.2f} meters", (obj.rect.left, obj.rect.top + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame with contours, QR code data, and distance
    cv2.imshow("Intel RealSense Camera", frame)

    # Break the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Stop the Intel RealSense pipeline
pipeline.stop()

# Close all OpenCV windows
cv2.destroyAllWindows()

# Now you can access the distance from the QR using the variable dist_QR
print(f"Distance from QR code: {dist_QR:.2f} meters")
