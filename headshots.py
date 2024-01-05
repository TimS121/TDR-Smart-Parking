import cv2  # OpenCV library for computer vision tasks

# Set the name for the directory where images will be saved
name = ''  # Replace with a specific name or leave empty

# Initialize the webcam (use 0 for default webcam)
cam = cv2.VideoCapture(0)

# Create a named window for displaying the camera feed
cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
cv2.resizeWindow("press space to take a photo", 500, 300)  # Resize the window

# Initialize image counter for naming the saved images
img_counter = 0

# Start capturing frames from the webcam
while True:
    ret, frame = cam.read()  # Read a frame from the webcam
    if not ret:
        print("failed to grab frame")  # Print error message if frame not grabbed
        break
    cv2.imshow("press space to take a photo", frame)  # Display the frame

    # Capture a keyboard input
    k = cv2.waitKey(1)
    if k % 256 == 27:  # ESC key pressed
        print("Escape hit, closing...")  # Print closing message
        break
    elif k % 256 == 32:  # SPACE key pressed
        # Save the captured image
        img_name = "dataset/" + name + "/image_{}.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)  # Write the frame to a file
        print("{} written!".format(img_name))  # Print confirmation message
        img_counter += 1  # Increment the image counter

# Release the webcam and destroy all OpenCV windows
cam.release()
cv2.destroyAllWindows()
