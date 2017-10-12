import json
import requests
from datetime import datetime
import subprocess
import sys
import base64
from scipy import misc
import base64
import json

if(len(sys.argv)<2):
  print("add one argument about which file to dump to show folder, camera01.png ~ camera13.png")
  exit()

# subprocess.check_output("cp /home/bowen/flask_venv/workspace/camera-icon/"+sys.argv[1]+" /tmp/detected_image_drop_for_web/",shell=True)

len_argv= len(sys.argv)
img_str_list=[]
for idx in range(1,len_argv):
  # img=misc.imread("/root/workspace/camera-icon/"+sys.argv[idx])
  # print type(img)
  # img_str_list.append(base64.b64encode(img.tostring()))
  with open("/root/workspace/camera-icon/"+sys.argv[idx]) as img_file:
    img_str_list.append(base64.b64encode(img_file.read()))

message_dict = {'updated_time':str(datetime.now()), 'event':'new_img', 'img_str_list':img_str_list}

# message_dict = {'updated_time':str(datetime.now()), 'event':'new_img', 'ms':'hahahahaha'}
message_json = json.dumps(message_dict)

res = requests.post("http://127.0.0.1:15020/pic", json=message_json)
print("normal pic transferred``")
