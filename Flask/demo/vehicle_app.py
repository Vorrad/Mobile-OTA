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
import demo.demo_primary as dp
import demo.demo_secondary as ds
from six.moves import xmlrpc_server
import readline, rlcompleter # for tab completion in interactive Python shell

app = Flask(__name__)
cors = CORS(app)

vehicle_running = 0


@app.route('/downloadUpdate', methods=['GET'])
def downloadUpdate():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        try:
            result  = dp.update_cycle()
            return jsonify({"code":200, "message":result})
        except Exception as r:
            print(r)
            return jsonify({"code":401, "message":"download error"})

@app.route('/startVehicle', methods=['GET'])
def startVehicle():
    res = []
    if request.method == 'OPTIONS':
        pass
    else:
        try:
            result = vehicle_start()
            return jsonify({"code":200, "message":result})
        except:
            return jsonify({"code":401, "message":"start error"})


def vehicle_start():
    global vehicle_running
    result = 'success'
    if vehicle_running == 0:
        dp.clean_slate()
        result = dp.update_cycle()
    print(result)
    vehicle_running = 1
    return result



if __name__ == '__main__':
    readline.parse_and_bind('tab: complete')
    # ota_start()
    app.run(host='0.0.0.0',port=8112)
