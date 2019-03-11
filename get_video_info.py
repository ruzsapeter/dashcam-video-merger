import json
import sys
from find_timestamp_with_ocr import extract_video_info

argc = len(sys.argv)
if (argc < 2):
    print("ERROR: missing argument")
    exit(-1)

# open video
video_file_name = sys.argv[1]

output = extract_video_info( video_file_name )

json_output = json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))
print(json_output)

exit (0)