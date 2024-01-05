import cv2  # OpenCV library for computer vision tasks
from picamera import PiCamera  # Library to control the Raspberry Pi Camera
from picamera.array import PiRGBArray  # For handling camera output to NumPy array

# Set the name for naming the captured images
name = 'Tim'  

# Initialize the camera
cam = PiCamera()
cam.resolution = (512, 304)  # Set the resolution of the camera
cam.framerate = 10  # Set the frame rate of the camera
rawCapture = PiRGBArray(cam, size=(512, 304))  # Create a PiRGBArray object

# Initialize image counter for naming the saved images
img_counter = 0

# Start capturing frames continuously
while True:
    for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = frame.array  # Convert the frame to a NumPy array
        cv2.imshow("Press Space to take a photo", image)  # Display the frame
        rawCapture.truncate(0)  # Clear the stream for the next frame

        # Capture a keyboard input
        k = cv2.waitKey(1)
        if k % 256 == 27:  # ESC key pressed
            break
        elif k % 256 == 32:  # SPACE key pressed
            # Save the captured image
            img_name = "dataset/" + name + "/image_{}.jpg".format(img_counter)
            cv2.imwrite(img_name, image)
            print("{} written!".format(img_name))
            img_counter += 1  # Increment the image counter
    
    # Break the loop if ESC key pressed
    if k % 256 == 27:
        print("Escape hit, closing...")
        break

# Destroy any OpenCV windows and release resources
cv2.destroyAllWindows()
