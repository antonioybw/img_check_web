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
import pymongo
from pymongo import MongoClient
import urllib
from bson import ObjectId
import hashlib, uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
#

detect_img_path='/root/workspace/img_check_web/static/img/detected/'
white_img_path='/root/workspace/img_check_web/static/img/white/'
black_img_path='/root/workspace/img_check_web/static/img/black/'
unknown_img_path='/root/workspace/img_check_web/static/img/unknown/'

#### database connection####


username = urllib.quote_plus('face_table_admin')
password = urllib.quote_plus('securitai_face135')
client = MongoClient("mongodb://%s:%s@184.105.242.130:19777/face_db"%(username, password))
db= client.face_db
whitelist=db.white_list_test
blacklist=db.black_list_test
unknownlist=db.unknown_list_test

## database user account##
user_db_username = urllib.quote_plus('user_admin')
user_db_password = urllib.quote_plus('securitai_user135')
user_db_client = MongoClient("mongodb://%s:%s@184.105.242.130:19777/user_db"%(user_db_username, user_db_password))
user_db= user_db_client.user_db


def init_path():
  path_all=[detect_img_path,white_img_path,black_img_path,unknown_img_path]
  for each in path_all:
    if not os.path.exists(each):
      subprocess.call('mkdir '+ each, shell=True)
    if not os.path.exists(each):
      return "img path not exists"
    subprocess.check_output("rm -rf "+each+"*",shell=True)


def find_img_list(detect_img_path=detect_img_path):
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


def save_image_to_static(img_str,save_path,img_id):
  item_b64_dec = base64.b64decode(img_str)
  with open(save_path+'new_img_'+img_id+'.png','wb') as imgfile:
    imgfile.write(item_b64_dec)
  # np_array = numpy.fromstring(item_b64_dec, numpy.uint8) 
  # np_array = np_array.reshape((160, 160, 3))
  # misc.imsave(save_path+'new_img_'+img_id+'.png', item_b64_dec)

def get_three_list():
  # get database list to display
  w_docs=whitelist.find()
  b_docs=blacklist.find()
  u_docs=unknownlist.find()
  w_list=[]
  b_list=[]
  u_list=[]
  for each_w in w_docs:
    save_image_to_static(each_w['face_icon'],white_img_path,str(each_w['_id']))
    w_list.append({'face_name':each_w['face_name'],'detected_time_list':each_w['detected_time_list'],'face_id':str(each_w['_id'])})
  for each_b in b_docs:
    save_image_to_static(each_b['face_icon'],black_img_path,str(each_b['_id']))
    b_list.append({'face_name':each_b['face_name'],'detected_time_list':each_b['detected_time_list'],'face_id':str(each_b['_id'])})
  for each_u in u_docs:
    save_image_to_static(each_u['face_icon'],unknown_img_path,str(each_u['_id']))
    u_list.append({'face_name':each_u['face_name'],'detected_time_list':each_u['detected_time_list'],'face_id':str(each_u['_id'])})
  return (w_list,b_list,u_list)


@app.route('/', methods = ['GET','POST']) # 
def user_feed():
  # sanity check about image path
  init_path()
  list_tuple=get_three_list();
  if request.method == 'POST':
    incoming_jsondata=request.get_json()
    message_dict=json.loads(incoming_jsondata)
    ### once there's new image uploaded
    print " got post from client"
    print "image string type is"
    print type(message_dict['img_str_list'][0])
    subprocess.check_output("rm -rf /root/workspace/img_check_web/static/img/detected/*",shell=True)
    if 'img_str_list' in message_dict:
      img_base64_list = message_dict['img_str_list']
      for idx,item in enumerate(img_base64_list):
        if message_dict['img_type']=='basic_base64':
          with open('/root/workspace/img_check_web/static/img/detected/new_img'+str(idx)+str(time.time())+'.png', 'w+') as img_file:
            img_file.write(base64.b64decode(item))
        else:
          with open('/root/workspace/img_check_web/static/img/detected/new_img'+str(idx)+str(time.time())+'.png', 'w+') as img_file:
            img_file.write(base64.b64decode(item)) 
          # item_b64_dec = base64.b64decode(item)
          # np_array = numpy.fromstring(item_b64_dec, numpy.uint8) 
          # np_array = np_array.reshape((160, 160, 3))
          # misc.imsave('/root/workspace/img_check_web/static/img/detected/new_img'+str(idx)+str(time.time())+'.png', np_array)
        
            
    if (message_dict['event']=='new_img'):
      img_list=find_img_list()
      send_to_client={}
      send_to_client['client_message']=message_dict
      send_to_client['img_list']=img_list
      socketio.emit('post detected',send_to_client)
  return render_template('user_feed.html',w_list=list_tuple[0],b_list=list_tuple[1],u_list=list_tuple[2])
  # return render_template('user_feed.html',b_list=b_list)
  # return render_template('user_feed.html',w_docs=w_docs,b_docs=b_docs,u_docs=u_docs)
  # return render_template('user_feed.html',w_dic=w_dic,b_dic=b_dic,u_dic=u_dic)


test_start_time= 0

@app.route('/display', methods = ['GET','POST']) # 
def get_img():
  subprocess.call('mkdir '+ detect_img_path,shell=True)
  if not os.path.exists(detect_img_path):
    return "img path not exists"
  subprocess.check_output("rm -rf /root/workspace/img_check_web/static/img/detected/*",shell=True)
  img_list=find_img_list()

  if request.method == 'POST':
    global test_start_time
    print "start time is"+str(test_start_time)
    cur_time=time.time()
    print "current time is"+str(cur_time)
    passed_time= (cur_time-test_start_time)
    print "current passed_time is:"+ str(passed_time)
    incoming_jsondata=request.get_json()
    message_dict=json.loads(incoming_jsondata)
    ### once there's new image uploaded
    print " got post from client"
    print "image string type is"
    print type(message_dict['img_str_list'][0])
    subprocess.check_output("rm -rf /root/workspace/img_check_web/static/img/detected/*",shell=True)
    if 'img_str_list' in message_dict:
      img_base64_list = message_dict['img_str_list']
      for idx,item in enumerate(img_base64_list):
          item_b64_dec = base64.b64decode(item)
          np_array = numpy.fromstring(item_b64_dec, numpy.uint8) 
          np_array = np_array.reshape((160, 160, 3))
          misc.imsave('/root/workspace/img_check_web/static/img/detected/new_img'+str(idx)+str(time.time())+'.png', np_array)
            
    if (message_dict['event']=='new_img'):
      img_list=find_img_list()
      send_to_client={}
      send_to_client['client_message']=message_dict
      send_to_client['img_list']=img_list
      socketio.emit('post detected',send_to_client)
  return render_template('detect_img.html',img_list=img_list)

@app.route('/set_time', methods = ['POST']) # 
def set_passed_time():
  global test_start_time
  test_start_time=time.time()
  print "time set ! the current start time is:"+ str(test_start_time)
  return "time set page"


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

@app.route('/login',methods = ['GET','POST'])
def login():
  return render_template('login.html')

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
  

# socket on part, receive data from client
@socketio.on('my event')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('insert_list')
def insert_to_database(message):
  db_toinsert=whitelist
  img_path=white_img_path
  if message['insert_type']=='white':
    db_toinsert=whitelist
    img_path=white_img_path
  elif message['insert_type']=='black':
    db_toinsert=blacklist
    img_path=black_img_path
  else:
    db_toinsert=unknownlist
    img_path=unknown_img_path
  # here the face icon is saved from the img_str_list, since it's the first time detected
  
  data_toinsert={'face_name':message['insert_data']['face_name_list'][0],
                  'face_icon':message['insert_data']['img_str_list'][0],
                  'face_feature':message['insert_data']['face_feature'],
                  'detected_time_list': [ message['insert_data']['updated_time']]}
  db_toinsert.insert_one(data_toinsert)
  all_docs=db_toinsert.find()
  # all_docs is a db cursor not array
  db_list=[]
  for each in all_docs:
    save_image_to_static(each['face_icon'],img_path,str(each['_id']))
    db_list.append({'face_name':each['face_name'],'detected_time_list':each['detected_time_list'],'face_id':str(each['_id'])})
  emit('update_db', {'type': message['insert_type'],'db_list':db_list})

@socketio.on('delete_item')
def delete_db_item(message):
  db_todelete=whitelist
  if message['delete_type']=='white':
    db_todelete=whitelist
  elif message['delete_type']=='black':
    db_todelete=blacklist
  else:
    db_todelete=unknownlist
  db_todelete.delete_one({'_id':ObjectId(message['delete_id'])})
  emit('finish_delete', {'line_id': message['line_id']})

@socketio.on('register')
def register_receive(message):
    print "receive register"
    print message
    salt=uuid.uuid4().hex
    message['salt']=salt
    hashed_password = hashlib.sha256(message['password']+salt).hexdigest()
    message['password']=hashed_password
    user_data_uuid=uuid.uuid4().hex
    message['face_doc_id']=message['user_name']+'-facelist-'+user_data_uuid
    message['user_FC_collection']=message['user_name']+'-FC-'+user_data_uuid
    print "insert data:"
    print message
    try:
      user_db.user_account.insert_one(message)
    except:
      print "error in user account insert"
      return
    new_face_list={
      "face_doc_id"         : message['face_doc_id'],
      "white_list"          : [],
      "black_list"          : [],
      "unknown_list"        : [],
      "user_FC_collection"  : message['user_FC_collection']
    }
    try:
      user_db.user_to_face.insert_one(new_face_list)
    except:
      print "error in user_to_face insert"
      return
    emit('success_register', {'username':message['user_name']})
    # emit('my response', {'data': message['data']})



if __name__ == '__main__':
    socketio.run(app,threaded=True)
