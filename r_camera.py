import cv2
import os

os.environ["DISPLAY"] = ":0.0"
# Open the camera (usually the default camera, 0)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Define the codec and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('/home/navkit/Desktop/output.avi', fourcc, 20.0, (640, 480))

while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if not ret:
        print("Error: Could not read frame.")
        break

    # Write the frame to the output video file
    out.write(frame)

    # Display the frame
    cv2.imshow('Camera Feed', frame)

    # Break the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera, close the output video file, and close the OpenCV window
cap.release()
out.release()
cv2.destroyAllWindows()
