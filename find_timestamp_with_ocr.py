try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

import cv2
print(cv2.__version__)

import re
import datetime
import json

import sys


def get_date_time_bboxes( image ):
    bbox_margin=4
    h, w, ch = image.shape
    # OCR + char bounding box    
    ocr_boxes_lines = pytesseract.image_to_boxes(image).splitlines()
    ocr_string=""

    for b in ocr_boxes_lines:
        words = b.split(' ')
        ocr_string += str(b[0])

    # locate date and time in string
    regex_date = re.compile(r"[0-9]{4}\/[0-9]{2}\/[0-9]{2}")
    regex_time = re.compile(r"[0-9]{2}:[0-9]{2}:[0-9]{2}")
    match_date = regex_date.search(ocr_string)
    match_time = regex_time.search(ocr_string)
    
    bb_date_start=ocr_boxes_lines[match_date.start()].split(' ')
    bb_date_end=ocr_boxes_lines[match_date.end()-1].split(' ')
    bb_time_start=ocr_boxes_lines[match_time.start()].split(' ')
    bb_time_end=ocr_boxes_lines[match_time.end()-1].split(' ')

    rect = list((int(bb_date_start[1]), h - int(bb_date_start[4]), int(bb_time_end[3]), h - int(bb_time_end[2])))

    date_split = ocr_string[match_date.start():match_date.end()].split('/')
    time_split = ocr_string[match_time.start():match_time.end()].split(':')

    timestamp = datetime.datetime(int(date_split[0]), int(date_split[1]), int(date_split[2]), int(time_split[0]), int(time_split[1]), int(time_split[2]))

    rect[0]=max(0, rect[0] - bbox_margin)
    rect[1]=max(0, rect[1] - bbox_margin)
    rect[2]=min(w - 1, rect[2] + bbox_margin)
    rect[3]=min(h - 1, rect[3] + bbox_margin)

    return (timestamp, rect)


argc = len(sys.argv)
if (argc < 2):
    print("ERROR: missing argument")
    exit -1

# open video
video_file_name = sys.argv[1]
vidcap = cv2.VideoCapture(video_file_name)
frame_counter = 0
success,image = vidcap.read()

# find first date + time stamp
ocr_result = get_date_time_bboxes(image)
ocr_bbox=ocr_result[1]
timestamp=ocr_result[0]

# for next frames crop only the timestamp area for OCR

while success:
    prev_timestamp=timestamp
    frame_counter += 1
    success,image = vidcap.read()
    if(frame_counter < 17):
        # DEBUG only
        continue
    cropped_image = image[ocr_bbox[1]:ocr_bbox[3],ocr_bbox[0]:ocr_bbox[2]]
    #cv2.imshow('image',cropped_image)
    #cv2.waitKey(0)
    ocr_result = get_date_time_bboxes(image)
    timestamp = ocr_result[0]
    # find first frame where timestamp changes
    timediff = timestamp - prev_timestamp
    if(datetime.timedelta(0) != timediff):
        output = {}
        output['FirstChangeAtFrame'] = str(frame_counter)
        output['Time'] = str(timestamp.strftime("%H:%M:%S"))
        output['Date'] = str(timestamp.strftime("%Y/%m/%d"))
        output['BoundingBox'] = str(ocr_bbox)


        json_output = json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))
        print(json_output)
        break
    #pts = vidcap.get(cv2.CAP_PROP_POS_MSEC)
    #print("frame PTS: ", pts, ", ", frame_counter, ": ", get_date_time_bboxes(cropped_image))

    if (60<=frame_counter):
        print("ERROR: no timestamp change in first 60 frames")
        exit -1
        break
