import sys
import json
import requests
from datetime import datetime
import base64
# img_dict = [{'input': 'hi', 'topic': 'Greeting'}]
with open("huawei.png", "rb") as imageFile:
  img_str = base64.b64encode(imageFile.read())
img_dict = {'updated_time':str(datetime.now()), 'img_str':img_str}
img_json = json.dumps(img_dict)
# s="hey yo test"
# res = requests.post("http://127.0.0.1:5001/img_data/", data=s).json()
res = requests.post("http://127.0.0.1:5001/", json=img_json)
print("updated")