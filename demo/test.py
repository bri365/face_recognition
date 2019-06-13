import glob
import os
import sys
import time

known_face_names = []
known_face_encodings = []

# Collect known images from this directory
# local_dir = os.path.dirname(os.path.realpath(__file__))
# local_images = glob('{}/*.jpg'.format(local_dir))
local_images = sorted(glob.glob('*.jpg'))
for image in local_images:
    # known_face_encodings.append(face_recognition.load_image_file(image))
    known_face_names.append(image[:-4])
exit()

face_locations = []
face_encodings = []
face_names = []
disconnect_count = 1
process_this_frame = 0
video_capture = None

while True:
    if video_capture is None:
        try:
            video_capture = ''
        except:
            if disconnect_count == 1:
                sys.stdout.write('Camera not available ')
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

        # Resize frame of video to 1/4 size for faster face recognition processing

        # Only process every other frame of video to save time
        if process_this_frame == 6:
            process_this_frame = 0
            # Find all the faces and face encodings in the current frame of video

        process_this_frame += 1
