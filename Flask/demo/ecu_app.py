from fileinput import filename
from sqlite3 import Timestamp
from unittest import result
from flask import Flask, jsonify, request,send_from_directory
import os
from flask_cors import CORS 
import datetime
import time
import json
import demo.demo_timeserver as dt
import demo.demo_director as dd
import demo.demo_image_repo as di
import demo.demo_secondary as ds
from six.moves import xmlrpc_server
import readline, rlcompleter # for tab completion in interactive Python shell

app = Flask(__name__)
cors = CORS(app)

ecu_running = 0


@app.route('/ecuUpdate', methods=['GET'])
def ecuUpdate():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        try:
            result  = ds.update_cycle()
            return jsonify({"code":200, "message":result})
        except Exception as r:
            print("\n\nerror!!",r)
            return jsonify({"code":401, "message":"update error"})

@app.route('/startECU', methods=['GET'])
def startECU():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        try:
            result = ECU_start()            
            return jsonify({"code":200, "message":result})
        except Exception as r:
            print("\n\nerror!!",r)
            return jsonify({"code":401, "message":"start error"})


def ECU_start():
    global ecu_running
    result = 'success'
    if ecu_running == 0:
        ds.clean_slate()
        time.sleep(0.5)
        result = ds.update_cycle()
    print(result)
    ecu_running = 1
    return result



if __name__ == '__main__':
    readline.parse_and_bind('tab: complete')
    # ota_start()
    app.run(host='0.0.0.0',port=8113)
