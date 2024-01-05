#! /usr/bin/python

# Import necessary libraries
import RPi.GPIO as GPIO  # For interfacing with GPIO pins on Raspberry Pi
import time  # For time-related functions
import threading  # For running tasks in parallel
from imutils.video import VideoStream, FPS  # For video stream and FPS calculation
import face_recognition  # For facial recognition features
import imutils  # For image processing utilities
import pickle  # For serializing and deserializing Python object structures
import cv2  # For OpenCV functionalities

# Initialize variables
currentname = "unknown"
encodingsP = "encodings.pickle"
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

# Initialize and start the video stream
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)  # Let the camera sensor warm up
fps = FPS().start()

# Servo motor setup
servoPin = 33  # GPIO pin for the servo motor
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(servoPin, GPIO.OUT)  # Set servoPin as an output pin
pwm = GPIO.PWM(servoPin, 50)  # Initialize PWM on servoPin at 50Hz frequency
pwm.start(7.5)  # Start PWM with 7.5% duty cycle (neutral position)

# Infrared (IR) sensor setup
ir_pin = 7  # GPIO pin for the IR sensor
GPIO.setup(ir_pin, GPIO.IN)  # Set ir_pin as an input pin

# Initialize flags and variables
camera_on = True
authorized_person_seen = False

# Function to control servo angle
def servo(angle):
    if not camera_on or not authorized_person_seen:
        return
    angle = max(-90, min(90, angle))  # Clamp angle to range [-90, 90]
    duty = 2.5 + (angle + 90) * (10 / 180)  # Calculate duty cycle
    pwm.ChangeDutyCycle(duty)

# Flag to manage door state
door_active = False

# Function to open and close the door
def open_door():
    global door_active
    if door_active:  # Check if door is already moving
        return

    door_active = True

    # Open door (move servo to 90 degrees)
    for degree in range(0, 91, 1):
        servo(degree)
        time.sleep(0.035)  # Smoother movement

    time.sleep(5)  # Keep door open for 5 seconds

    # Close door (move servo back to 0 degrees)
    for degree in range(90, -1, -1):
        servo(degree)
        time.sleep(0.035)  # Smoother movement

    pwm.ChangeDutyCycle(7.5)  # Reset servo to neutral position
    door_active = False

# List of recognized names
recognized_names = ["Tim", "Ravin", "Dhanraj"]
last_print_time = time.time()

# Main loop
while True:
    # Check if IR sensor detects an obstacle
    if GPIO.input(ir_pin) == GPIO.LOW:
        # Restart PWM if it stopped
        if not pwm:
            pwm = GPIO.PWM(servoPin, 50)
            pwm.start(0)

        print("IR Sensor detected an obstacle")

        # Face recognition processing
        frame = vs.read()
        frame = imutils.resize(frame, width=500)
        small_frame = imutils.resize(frame, width=250)
        boxes = face_recognition.face_locations(small_frame)
        encodings = face_recognition.face_encodings(small_frame, boxes)
        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown"
            if True in matches:
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1
                name = max(counts, key=counts.get)
                names.append(name)

        # Check if a recognized person is seen
        for detected_name in names:
            if detected_name in recognized_names:
                authorized_person_seen = True
                if not door_active:
                    threading.Thread(target=open_door).start()

        # Draw rectangles and names on faces
        for ((top, right, bottom, left), name) in zip(boxes, names):
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)

        # Display the frame
        cv2.imshow("Facial Recognition is Running", frame)
        key = cv2.waitKey(1) & 0xFF

        # Break from the loop if 'q' key is pressed
        if key == ord("q"):
            break

        fps.update()
    else:
        # Print IR sensor status every 10 seconds if no obstacle is detected
        current_time = time.time()
        if current_time - last_print_time >= 10:
            print("IR Sensor is not detecting an obstacle")
            last_print_time = current_time

# Clean up
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
if door_active:
    pwm.stop()
GPIO.cleanup()
cv2.destroyAllWindows()
vs.stop()
