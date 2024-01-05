#! /usr/bin/python

# Importing necessary libraries
from imutils.video import VideoStream, FPS  # Utilities for working with video streams
import face_recognition  # Library for facial recognition
import imutils  # Library for image processing
import pickle  # Module to serialize/deserialize Python object structures
import time  # Module for time-related functions
import cv2  # OpenCV library for computer vision tasks

# Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"

# Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"

# Load the known faces and embeddings along with OpenCV's Haar cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())

# Initialize the video stream and allow the camera sensor to warm up
# Note: src=0 for built-in webcam, src=2 or other number for external cameras
# Use `usePiCamera=True` for Raspberry Pi camera module
vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)  # Wait for 2 seconds to let the camera sensor warm up

# Start the FPS counter
fps = FPS().start()

# Loop over frames from the video stream
while True:
    # Grab the frame from the video stream and resize it to 500px width to speed up processing
    frame = vs.read()
    frame = imutils.resize(frame, width=500)

    # Detect face locations in the frame
    boxes = face_recognition.face_locations(frame)

    # Compute the facial embeddings for each detected face
    encodings = face_recognition.face_encodings(frame, boxes)
    names = []

    # Loop over the facial embeddings
    for encoding in encodings:
        # Attempt to match each face in the input image to known encodings
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"  # Default to "Unknown" if face is not recognized

        # Check if we have found a match
        if True in matches:
            # Find indexes of all matched faces and count the total number of times each face was matched
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            # Count each recognized face
            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            # Determine the recognized face with the largest number of votes
            name = max(counts, key=counts.get)

            # Print the name if a new person is identified
            if currentname != name:
                currentname = name
                print(currentname)

        # Update the list of names
        names.append(name)

    # Loop over the recognized faces
    for ((top, right, bottom, left), name) in zip(boxes, names):
        # Draw rectangles and names around the faces
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 225), 2)
        y = top - 15 if top - 15 > 15 else top + 15
        cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    # Display the image with face detections
    cv2.imshow("Facial Recognition is Running", frame)
    key = cv2.waitKey(1) & 0xFF

    # Break from the loop when 'q' key is pressed
    if key == ord("q"):
        break

    # Update the FPS counter
    fps.update()

# Stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# Cleanup: close all windows and stop video stream
cv2.destroyAllWindows()
vs.stop()
