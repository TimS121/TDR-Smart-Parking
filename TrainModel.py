#! /usr/bin/python

# Importing necessary libraries
from imutils import paths  # Utility functions for working with image paths
import face_recognition  # Library for face recognition
import pickle  # Module for serializing and deserializing Python object structures
import cv2  # OpenCV library for image processing
import os  # Library for interacting with the operating system

# Indicate start of process
print("[INFO] start processing faces...")

# Getting the list of image paths from the dataset folder
imagePaths = list(paths.list_images("dataset"))

# Initialize lists to hold the facial encodings and corresponding names
knownEncodings = []
knownNames = []

# Loop over each image path in the dataset
for (i, imagePath) in enumerate(imagePaths):
    # Print progress information
    print("[INFO] processing image {}/{}".format(i + 1, len(imagePaths)))

    # Extract the person's name from the image path
    name = imagePath.split(os.path.sep)[-2]

    # Load the image and convert it from BGR (OpenCV format) to RGB
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Detect the coordinates of faces in the image
    boxes = face_recognition.face_locations(rgb, model="hog")

    # Compute the facial embedding for each detected face
    encodings = face_recognition.face_encodings(rgb, boxes)

    # Loop over each encoding and associate it with the person's name
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

# Serialize the facial encodings and names to disk
print("[INFO] serializing encodings...")
data = {"encodings": knownEncodings, "names": knownNames}
with open("encodings.pickle", "wb") as f:
    pickle.dump(data, f)
