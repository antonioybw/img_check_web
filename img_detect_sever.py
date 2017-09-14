from flask import Flask,render_template
from flask import request
import json
import os
import time
import base64

detect_img_path='/tmp/detected_face/'
cfg_file_path='/tmp/cfg'

app = Flask(__name__) 

@app.route('/', methods = ['GET','POST']) # 
def get_img():
  if not os.path.exists(detect_img_path):
    return "img path not exists"

  img_list=[]
  for file in os.listdir(detect_img_path):
    if file.endswith('.png') or file.endswith('.jpg'):
      file_path = os.path.join(detect_img_path, file)
      try:
        create_time= time.ctime(os.path.getctime(file_path))
      except OSError:
        create_time= 0
      with open(file_path, "rb") as imageFile:
        img_str = base64.b64encode(imageFile.read())
      img_list.append({'create_time':create_time,'img_str':img_str})

  if not os.path.exists(cfg_file_path):
    f=file(cfg_file_path,'w')
    json.dump({},f)

  with open(cfg_file_path,'r') as f:
    param_dict = json.load(f)

  return render_template('detect_img.html',img_list=img_list,param=param_dict)

if __name__ == '__main__':
    app.run(debug=True)