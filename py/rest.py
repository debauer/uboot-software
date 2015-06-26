#!/usr/bin/python
#
# Status: Tested
#
from flask import Flask, jsonify
import pymongo
from pymongo import MongoClient
#from elasticsearch import Elasticsearch
from flask import request
from bson import BSON
from bson import json_util
import time
from datetime import datetime
#from influxdb import InfluxDBClient
from influxdb.influxdb08 import InfluxDBClient
import psutil
import json
from thread import start_new_thread
from termcolor import colored

mongo = MongoClient()
#mongo = MongoClient('mongodb://localhost:27017/')

config = json.loads(open('../configs/aor_service.json').read())
db_influx = InfluxDBClient(config['influx']['host'],
	config['influx']['port'],
	config['influx']['user'],
	config['influx']['pw'],
	config['influx']['db'])

db_mongo = mongo.rallye
values = db_mongo.values
app = Flask(__name__)
#es = Elasticsearch()

hostname = config['hostname']
logging = False

# curl -i http://127.0.0.1:5002/api/v1.0/value
@app.route('/api/v1.0/ping', methods=['get'])
def get_ping():
	doc = values.find()
	return "OK", 201

@app.route('/api/v1.0/ping', methods=['post'])
def post_ping():
	doc = values.find()
	return "OK", 201

# curl -i http://127.0.0.1:5002/api/v1.0/value
@app.route('/api/v1.0/value', methods=['get'])
def get_values():
	doc = values.find()
	return json_util.dumps(doc, sort_keys=True, indent=4, default=json_util.default), 201


# curl -i http://127.0.0.1:5002/api/v1.0/value/aussen
@app.route('/api/v1.0/value/<string:key>', methods=['get'])
def get_value(key):
	doc = values.find_one({"key":key})
	return json_util.dumps(doc, sort_keys=True, indent=4, default=json_util.default), 201

# curl -i -H "Content-Type: application/json" -X POST -d '{"key":"aussen", "value":123.2}' http://127.0.0.1:5002/api/v1.0/value
@app.route('/api/v1.0/value', methods=['POST'])
def post_value():
	if not request.json or not 'key' in request.json or not 'value' in request.json:
		abort(400)
	values.update({'key':request.json.get("key")},request.json,True)
	doc = values.find_one({"key":request.json.get("key")})
	return json_util.dumps(doc, sort_keys=True, indent=4, default=json_util.default), 201

if __name__ == '__main__':

	#app.run(host="192.168.3.184",port=5002,debug=True)
	app.run(port=5002,debug=True)

	#!/usr/bin/python


