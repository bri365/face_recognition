import glob
import os
import sys
import time

import cv2
import face_recognition
import numpy as np

disconnect_count = 1
face_encodings = []
face_locations = []
face_names = []
known_face_encodings = []
known_face_names = []
process_this_frame = 0
video_capture = None

# Collect known images from this directory
local_images = sorted(glob.glob('*.jpg'))
for image in local_images:
    known_face_encodings.append(face_recognition.load_image_file(image))
    known_face_names.append(image[:-4])

# Loop until 'q' pressed on keyboard
while True:
    if video_capture is None:
        try:
            # Dahau camera
            # video_capture = cv2.VideoCapture('rtsp://admin2:P@ssw0rd@192.168.1.108:554//cam/realmonitor?channel=1&subtype=0')
            # Reolink camera
            video_capture = cv2.VideoCapture('rtsp://admin:admin@172.16.50.32:554//h264Preview_01_main')
        except:
            if disconnect_count == 1:
                sys.stdout.write("Camera not available ('q' to quit) ")
            else:
                sys.stdout.write('.')
                if disconnect_count == 60:
                    sys.stdout.write('\n')
                    disconnect_count = 0
                disconnect_count += 1
            sys.stdout.flush()
            time.sleep(5)
    else:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        
        # Flip frame for ceiling mount camera sitting on a table
        cv2.flip(frame, -1, frame)

        # Resize frame to fit on screen
        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Create 1/4 size frame for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process a few video frames to save time (one in every 6)
        if process_this_frame == 6:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                name = "Unknown"

                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

            process_this_frame = 0

        process_this_frame += 1

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)

    # 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to camera and remove image window
try:
    video_capture.release()
    cv2.destroyAllWindows()
except:
    pass
