'''
Author: your name
Date: 2022-04-28 19:32:30
LastEditTime: 2022-04-30 14:10:03
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: \test_flask\hello.py
'''
from fileinput import filename
from sqlite3 import Timestamp
from flask import Flask, jsonify, request,send_from_directory
import os
from flask_cors import CORS 
import datetime
import time
import json

import demo.demo_image_repo as di
import demo.demo_director as dd
import demo.demo_timeserver as dt

app = Flask(__name__)
cors = CORS(app)

image_dic = []
update_config_list = []


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/uploadFile', methods=['POST'])
def uploadFile():
    if request.method == 'OPTIONS':
        pass
    else:
        attfile = request.files.get('file')
        save_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'file')
        print(attfile.filename,type(attfile),save_path)
        attfile.save(os.path.join(save_path, attfile.filename))
 
    return   {"code":200, "message":"上传请求成功", "filename":attfile.filename}

@app.route('/uploadImageName', methods=['POST'])
def uploadImageName():
    if request.method == 'OPTIONS':
        pass
    else:
        data = eval(request.data.decode())
        name = data['name']
        filename = data['filename']
        global image_dic
        image_dic.append(
            {
                'name': name,
                'filename': filename,
                'time': str(datetime.datetime.today())[:-7]
            }
        )
    return   {"code":200, "message":"上传请求成功","filename":filename,"name":name}

@app.route('/getImageList', methods=['GET'])
def getImageList():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        global image_dic
        res = image_dic
 
    return jsonify(res)


@app.route('/postUpdateConfig', methods=['POST'])
def postUpdateConfig():
    if request.method == 'OPTIONS':
        pass
    else:
        data = eval(request.data.decode())
        # timestamp = data['timestamp']
        # 13 bit timestamp
        timestamp = int(round(time.time() * 1000))
        due_time = time_convert(timestamp/1000)
        data['datetime'] = due_time
        update_config_list.append(data)
        print(update_config_list)
        save_update_config()

    return   {"code":200, "message":"上传请求成功"}

@app.route('/getUpdateConfig', methods=['GET'])
def getUpdateConfig():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        global update_config_list
        res = update_config_list
 
    return jsonify(res)


def time_convert(timestamp):
    timelocal = time.localtime(timestamp)
    due_time = time.strftime("%Y-%m-%d %H:%M:%S", timelocal)
    return due_time

def save_update_config():
    global update_config_list
    f = open('update_config_list.json','w')
    json.dump(update_config_list, f)
    f.close()
    return

def load_update_config():
    global update_config_list
    update_config_list = json.load(open('test.update_config_list','r'))
    return

if __name__ == '__main__':
    # load_update_config()
    
    di.clean_slate()

    dd.clean_slate()

    dt.listen()

    # if activate debug, server would duplicate running.
    # app.debug = True

    app.run()