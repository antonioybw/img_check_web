import json
import requests
from datetime import datetime
import subprocess
import sys
import base64
from scipy import misc
import base64
import json
##
if(len(sys.argv)<3):
  print("first argument as image type")
  print("following arguments about which file to dump to show folder, camera01.png ~ camera13.png")
  exit()

# subprocess.check_output("cp /home/bowen/flask_venv/workspace/camera-icon/"+sys.argv[1]+" /tmp/detected_image_drop_for_web/",shell=True)

len_argv= len(sys.argv)
img_str_list=[]
for idx in range(2,len_argv):
  # img=misc.imread("/root/workspace/camera-icon/"+sys.argv[idx])
  # print type(img)
  # img_str_list.append(base64.b64encode(img.tostring()))
  with open("/root/workspace/camera-icon/"+sys.argv[idx]) as img_file:
    img_str_list.append(base64.b64encode(img_file.read()))

# message_dict = {'updated_time':str(datetime.now()), 'event':'new_img', 'img_str_list':img_str_list, 'img_type':'basic_base64'}
message_dict = {'updated_time':str(datetime.now()), 
                'event':'new_img', 
                'img_str_list':img_str_list, 
                'img_type':'basic_base64',
                'face_icon':'',
                'face_feature':'',
                'type':'unknown',
                'face_name_list':['']}
message_dict['type']=sys.argv[1]


# message_dict = {'updated_time':str(datetime.now()), 'event':'new_img', 'ms':'hahahahaha'}
message_json = json.dumps(message_dict)

res = requests.post("http://172.17.0.12:15020", json=message_json)
print("normal pic transferred``")
