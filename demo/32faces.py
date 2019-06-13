import glob
import os
import socket
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
            s = socket.create_connection(address=('172.16.50.32', 554), timeout=2)
            s.close()
            # Dahau camera
            video_capture = cv2.VideoCapture('rtsp://admin:password@172.16.50.32:554//h264Preview_01_main')
            # Reolink camera
            # video_capture = cv2.VideoCapture('rtsp://admin2:P@ssw0rd@192.168.1.108:554//cam/realmonitor?channel=1&subtype=0')
            # Grab and resize a single frame of video to ensure connection works
            # print('1 capture frame')
            ret, frame = video_capture.read()
            # print('1 resize frame')
            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        except KeyboardInterrupt:
            exit()
        except:
            video_capture = None
            if disconnect_count == 1:
                sys.stdout.write("Camera not available ('^C' to quit) ")
            else:
                sys.stdout.write('.')
                if disconnect_count == 30:
                    sys.stdout.write('\n')
                    disconnect_count = 0

            disconnect_count += 1
            sys.stdout.flush()
            time.sleep(3)
    else:
        try:
            # Grab a single frame of video
            # print('2 capture frame')
            ret, frame = video_capture.read()

            # Flip frame for ceiling mount camera sitting on a table
            # print('2 flip frame')
            cv2.flip(frame, -1, frame)

            # Resize frame to fit on screen
            # print('2 resize frame')
            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            # Only process a few video frames to save time (one in every 6)
            if process_this_frame == 6:
                # Create 1/4 size frame for faster face recognition processing
                # print('2 small frame')
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                # print('2 rgb frame')
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                # print('2 faces locations')
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
            # print('2 show image')
            cv2.imshow('Video', frame)
        except KeyboardInterrupt:
            exit()
        except:
            try:
                disconnect_count = 1
                video_capture.release()
                cv2.destroyAllWindows()
            except:
                pass
            video_capture = None

    # Suppose to detect 'q' on the keyboard, but it doesn't seem to work
    # However it does appear to be needed for the video to be displayed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        try:
            video_capture.release()
            cv2.destroyAllWindows()
        except:
            pass
        exit()
