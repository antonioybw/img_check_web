from flask import Flask,render_template
from flask import request
import json
import os
import time
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit
import subprocess
import time
from scipy import misc
import numpy
import scipy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


detect_img_path='/root/workspace/img_check_web/static/img/'

def find_img_list():
  img_list=[]
  for file in os.listdir(detect_img_path):
    if file.endswith('.png') or file.endswith('.jpg'):
      file_path = os.path.join(detect_img_path, file)
      try:
        create_time= time.ctime(os.path.getctime(file_path))
      except OSError:
        create_time= 0
      img_list.append({'create_time':create_time,'img_path':file})
  return img_list


@app.route('/', methods = ['GET','POST']) # 
def get_img():
  subprocess.call('mkdir '+ detect_img_path,shell=True)
  if not os.path.exists(detect_img_path):
    return "img path not exists"
  subprocess.check_output("rm -rf /root/workspace/img_check_web/static/img/*",shell=True)
  img_list=find_img_list()

  if request.method == 'POST':
    incoming_jsondata=request.get_json()
    message_dict=json.loads(incoming_jsondata)
    ### once there's new image uploaded
    print " got post from client"
    print "image string type is"
    print type(message_dict['img_str_list'][0])
    subprocess.check_output("rm -rf /root/workspace/img_check_web/static/img/*",shell=True)
    if 'img_str_list' in message_dict:
      img_base64_list = message_dict['img_str_list']
      for idx,item in enumerate(img_base64_list):
        #if isinstance(item,unicode):
         # print "reach type:"
          #print type(item)
          #with open('/root/workspace/img_check_web/static/img/new_img'+str(idx)+str(time.time())+'.png', 'w') as img_file:
            #img_file.write(item.decode('base64'))
        #else: 
        print "reach type:"
        print type(item)
        print 'item', item
        item_b64_dec = base64.b64decode(item)
        print 'type, item b64 dec', type(item_b64_dec) 
        np_array = numpy.fromstring(item_b64_dec, numpy.uint8) 
        np_array = np_array.reshape((160, 160, 3))
        #item_b64_dec_np = numpy.fromstring(item_b64_dec) 
        #np_array=numpy.fromstring(item.decode('base64'))
        print np_array.shape
        print "type from string"
        print type(np_array)
        misc.imsave('/root/workspace/img_check_web/static/img/new_img'+str(idx)+str(time.time())+'.png', np_array)
        #img = scipy.misc.toimage(np_array)
        #img.save('/root/workspace/img_check_web/static/img/new_img'+str(idx)+str(time.time())+'.png')
            
    if (message_dict['event']=='new_img'):
      img_list=find_img_list()
      send_to_client={}
      send_to_client['client_message']=message_dict
      send_to_client['img_list']=img_list
      socketio.emit('post detected',send_to_client)
  return render_template('detect_img.html',img_list=img_list)


@app.route('/info', methods = ['POST']) # 
def get_message():
  if request.method == 'POST':
    incoming_jsondata=request.get_json()
    message_dict=json.loads(incoming_jsondata)
    print message_dict
    return "ok"
@app.route('/test')
def show():
  return 'haha'

@app.route('/pic', methods = ['POST']) # 
def get_normal_pic():
  if request.method == 'POST':
    incoming_jsondata=request.get_json()
    message_dict=json.loads(incoming_jsondata)
    ### once there's new image uploaded
    print " got post from client"
    print "image string type is"
    print type(message_dict['img_str_list'][0])
    subprocess.check_output("rm -rf /root/workspace/img_check_web/static/img/*",shell=True)
    if 'img_str_list' in message_dict:
      img_base64_list = message_dict['img_str_list']
      for idx,item in enumerate(img_base64_list):
        print "reach type:"
        print type(item)
        with open('/root/workspace/img_check_web/static/img/new_img'+str(idx)+str(time.time())+'.png', 'w') as img_file:
          img_file.write(base64.b64decode(item))
        
            
    if (message_dict['event']=='new_img'):
      img_list=find_img_list()
      send_to_client={}
      send_to_client['client_message']=message_dict
      send_to_client['img_list']=img_list
      socketio.emit('post detected',send_to_client)
  return "ok"


@app.route('/show_path_img', methods = ['GET','POST']) # 
def get_img_from_path():
  detect_img_path='/tmp/detected_face/'
  cfg_file_path='/tmp/cfg'
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
  

@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': message['data']})

if __name__ == '__main__':
    socketio.run(app,threaded=True)
