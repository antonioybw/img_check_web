from flask import Flask,render_template
from flask import request
import json
import os

detect_img_path='/tmp/detected_img'
cfg_file_path='/tmp/cfg'

app = Flask(__name__) 

@app.route('/', methods = ['GET','POST']) # 
def get_img():
  if not os.path.exists(detect_img_path):
    f=file(detect_img_path,'w')
    json.dump({},f)

  if not os.path.exists(cfg_file_path):
    f=file(cfg_file_path,'w')
    json.dump({},f)

  if request.method == 'POST':
    incoming_jsondata=request.get_json()
    img_data=json.loads(incoming_jsondata)
    with open(detect_img_path,'w') as img_f:
      json.dump(img_data,img_f)

  with open(cfg_file_path,'r') as f:
    param_dict = json.load(f)

  with open(detect_img_path,'r') as f:
    img_dict = json.load(f)
  return render_template('detect_img.html',img_dict=img_dict,param=param_dict)

if __name__ == '__main__':
    app.run(debug=True)