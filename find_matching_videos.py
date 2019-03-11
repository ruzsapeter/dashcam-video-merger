import re
import datetime
import json
import sys
import glob
import os
from find_timestamp_with_ocr import extract_video_info

argc = len(sys.argv)
if (argc < 2):
    print("ERROR: missing argument")
    exit(-1)

# list video files from directory
directory_name = os.path.realpath(sys.argv[1])
#file_info_storage = directory_name + "/file_info.json"

print("Working in directory ", directory_name)

all_files = glob.glob(directory_name + '/*')

regexs = [re.compile(r"[0-9]{4}_[0-9]{4}_[0-9]{6}_[0-9]{3}\.MP4"), re.compile(r"MOV_[0-9]{4}\.MOV")]

selected_filenames = [[], []]

for filename in all_files:
    for i in range(len(regexs)):
        if(regexs[i].search(filename)):
            selected_filenames[i].append(filename)
        continue

print("Found front files:")
print(selected_filenames[0])

print("Found rear files:")
print(selected_filenames[1])

video_infos = [[], []]
for group_idx in range(len(selected_filenames)):
   for i in range(len(selected_filenames[group_idx])):
       print(selected_filenames[group_idx][i])
       entry = {}
       entry['Filename'] = selected_filenames[group_idx][i]
       entry['VideoInfo'] = extract_video_info(selected_filenames[group_idx][i])
       video_infos[group_idx].append(entry)

json_output = json.dumps(video_infos, sort_keys=True, indent=4, separators=(',', ': '))
print(json_output)
#print( video_infos )

