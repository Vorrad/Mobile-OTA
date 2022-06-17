from cgi import print_arguments
from fileinput import filename
from sqlite3 import Timestamp
from sre_constants import FAILURE, SUCCESS
from django.http import Http404, HttpResponse
from flask import Flask, jsonify, request,send_from_directory
import os
from flask_cors import CORS 
import datetime
import time
import json
import demo.demo_timeserver as dt
import demo.demo_director as dd
import demo.demo_image_repo as di
from six.moves import xmlrpc_server
import readline, rlcompleter # for tab completion in interactive Python shell
import requests

app = Flask(__name__)
cors = CORS(app)

IMAGE_ROOTPATH = "../Django/media"

image_dic = []
update_config_list = []
new_update_config= []

@app.route("/")
def hello_world():
    return "<p>后端服务器首页</p>"

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
        print("\n\ndata:", data)
        data = dict(data)
        data["time"] = str(datetime.datetime.today())[:-7]
        global image_dic
        image_dic.append(data)

    return   {"code":200, "message":"上传请求成功"}

@app.route('/deleteImageName', methods=['POST'])
def deleteImageName():
    if request.method == 'OPTIONS':
        pass
    else:
        data = eval(request.data.decode())
        data = dict(data)
        name = data["name"]
        global image_dic
        image_num = len(image_dic)
        image_dic = [item for item in image_dic if not item["name"] == name]
        if image_num != len(image_dic):
            return {"code":200, "message":"删除成功"}
        else:
            return {"code":500, "message":"删除失败"}

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
        timestamp = data['timestamp']
        due_time = time_convert(timestamp/1000)
        data['datetime'] = due_time
        global update_config_list
        global new_update_config
        new_update_config = data
        update_config_list.append(data)
        save_update_config()
        # diliver_update(data)

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

@app.route('/getNewUpdate', methods=['GET'])
def getNewUpdate():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        global new_update_config
        res = new_update_config
 
    return jsonify(res)

@app.route('/deliverUpdate', methods=['GET'])
def deliverUpdate():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        global new_update_config
        try:
            stat = deliver_update(new_update_config)
            if stat == SUCCESS:
                return jsonify({"code":200, "message":"下发镜像成功"})
            else:
                return jsonify({"code":500, "message":"下发镜像失败"})                
        except Exception as r:
            print("\nError:", r, "\n")
            return jsonify({"code":401, "message":"deliver error"})

@app.route('/refresh', methods=['POST'])
def refresh():
    res = []
    data = eval(request.data.decode())
    print(data)
    if request.method == 'OPTIONS':
        pass
    else:
        if data['update_type'] == 'man_in_middle':
            dd.undo_mitm_arbitrary_package_attack('democar', 'firmware.img')
        elif data['update_type'] == 'replace':
            di.undo_mitm_arbitrary_package_attack('firmware.img')
        elif data['update_type'] == 'replay':
            dd.restore_timestamp('democar')
        return jsonify({"code":200, "message":"刷新成功"})


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
    update_config_list = json.load(open('update_config_list.json','r'))
    global new_update_config
    new_update_config = update_config_list[-1]
    return

def deliver_update(config):
    try :    
        global image_dic

        vin = config['vin']
        ecu_name = config['ecu_name']
        image_name = config['update_image_name']
        print("\nvin = ", vin, "ecu_name = ", ecu_name,"update_image_name = ", image_name)
        print("image_dic: ", image_dic)

        image_found = False
        for image in image_dic:
            if image_name == image["name"]:
                image_file_name = image["filename"]
                image_found = True
                break
        if not image_found:
            return {"code":404, "message":"未找到该图像"}
        else:
            print("\n找到图像文件")

        
        image_path = IMAGE_ROOTPATH + '/' + image_file_name
        print(image_path)
        if config['update_type'] == 'normal':
            print("normal diliver update")
            di.add_target_to_imagerepo(image_path, image_name)
            di.write_to_live()
            dd.add_target_to_director(image_path, image_name, vin, ecu_name)
            dd.write_to_live(vin_to_update=vin)
        elif config['update_type'] == 'man_in_middle':
            dd.mitm_arbitrary_package_attack(vin, 'firmware.img')
        elif config['update_type'] == 'replace':
            di.mitm_arbitrary_package_attack('firmware.img')
        elif config['update_type'] == 'replay':
            dd.backup_timestamp(vin)
            dd.write_to_live(vin)
            requests.get(url='http://192.168.209.133:8112/downloadUpdate')   
            dd.replay_timestamp(vin)
        elif config['update_type'] == 'director_leak':
            dd.add_target_and_write_to_live(filename='firmware.img',
        file_content='evil content', vin=vin, ecu_serial=ecu_name)

        else:
            dd.add_target_and_write_to_live(filename='firmware.img',
        file_content='evil content', vin=vin, ecu_serial=ecu_name)
            di.add_target_and_write_to_live(filename='firmware.img', file_content='evil content')
        return SUCCESS
    except Exception as e:
        print("\nDeliverUpdate ERROR:", e, "\n")
        return FAILURE

def ota_start():

    # Start demo Image Repo, including http server and xmlrpc listener (for
    # webdemo)
    di.clean_slate()

    # Start demo Director, including http server and xmlrpc listener (for
    # manifests, registrations, and webdemo)
    dd.clean_slate()

    # Start demo Timeserver, including xmlrpc listener (for requests from demo
    # Primary)
    dt.listen()

    firmware_fname = filepath_in_repo = 'firmware.img'
    open(firmware_fname, 'w').write('Fresh firmware image')
    di.add_target_to_imagerepo(firmware_fname, filepath_in_repo)
    di.write_to_live()
    vin='democar'; ecu_serial='TCUdemocar'
    dd.add_target_to_director(firmware_fname, filepath_in_repo, vin, ecu_serial)
    dd.write_to_live(vin_to_update=vin)

if __name__ == '__main__':
    load_update_config()
    readline.parse_and_bind('tab: complete')
    ota_start()
    app.run(host='0.0.0.0',port=8111)
