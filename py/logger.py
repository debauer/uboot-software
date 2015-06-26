#!/usr/bin/python
#
# Status: Tested
#
import psutil
import json
import sys
import requests
import requests.exceptions
import time
import gc
#from flask import Flask, jsonify, request
from bson import BSON
from bson import json_util
from datetime import datetime
#from thread import start_new_thread
from termcolor import colored

import logging
import logging.handlers
import argparse

# Deafults
LOG_FILENAME = "/var/log/aor/logger.log"
LOG_LEVEL = logging.DEBUG  # Could be e.g. "DEBUG" or "WARNING"

parser = argparse.ArgumentParser(description="My simple Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
parser.add_argument("-n", "--nolog", help="no log, use stdio", default=False, action="store_true")

args = parser.parse_args()
if args.log:
	LOG_FILENAME = args.log

if not args.nolog:
	logger = logging.getLogger(__name__)
	logger.setLevel(LOG_LEVEL)
	handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
	formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	
	class MyLogger(object):
		def __init__(self, logger, level):
			"""Needs a logger and a logger level."""
			self.logger = logger
			self.level = level
	 
		def write(self, message):
			# Only log if there is a message (not just a new line)
			if message.rstrip() != "":
				self.logger.log(self.level, message.rstrip())
	 
	# Replace stdout with logging to file at INFO level
	sys.stdout = MyLogger(logger, logging.INFO)
	# Replace stderr with logging to file at ERROR level
	sys.stderr = MyLogger(logger, logging.ERROR)

config = json.loads(open('/home/debauer/AOR2015/configs/aor_service.json').read())

logging_info = config['logging']['logger']['info']
logging_error = config['logging']['logger']['error']
store_mongo = config['store']['mongo']
store_influx = config['store']['influx']
store_redis = config['store']['redis']
store_rrd = config['store']['rrd']
hostname = config['hostname']


auto_anzahl = config['autos']['anzahl']
auto_sensoren = {}
auto_sensoren[0] = config['autos']['sensoren']['auto0']
auto_sensoren[1] = config['autos']['sensoren']['auto0']
auto_sensoren[2] = config['autos']['sensoren']['auto0']

exchange_store = "mongo"	# mongo oder redis

if(store_rrd):
	import rrdtool

if(store_mongo):
	import pymongo
	mongo = pymongo.MongoClient()
	#mongo = MongoClient('mongodb://localhost:27017/')
	mongo_db = mongo.rallye
	mongo_values = mongo_db.values

#if(store_keyvalue == "redis"):
if(store_influx):
	#from influxdb import InfluxDBClient
	from influxdb.influxdb08 import InfluxDBClient
	from influxdb.influxdb08.client import InfluxDBClientError
	influx_db = InfluxDBClient(config['influx']['host'],config['influx']['port'],config['influx']['user'],config['influx']['pw'],config['influx']['db'])

#app = Flask(__name__)

#es.indices.create(index='system-index', ignore=400)

values = {}
values["cpu"] = {}
values["ram"] = {}
values["mpd"] = {}
values["1wire"] = {}
values["disk"] = {}
series = []

def print_logger(str):
	if(logging_info):
		print colored("logger:", 'cyan'), colored(str, 'magenta')

def print_logger_error(str):
	if(logging_error):
		print colored("error:", 'red'), colored(str, 'magenta')

def print_influx_ConnectionError():
	print_logger_error("INFLUX ConnectionError")

def print_influx_ClientError():
	print_logger_error("INFLUX ClientError")

def influx_write_series():
	global series
	if(store_influx):
		try:
			influx_db.write_points(series)
			series = []
		except InfluxDBClientError:
			print_influx_ClientError()
		except requests.exceptions.ConnectionError:
			print_influx_ConnectionError()
	else:
		series = []

def mongo_update(key,value):
	if(store_mongo):
		mongo_values.update({'key':key},{"key": key,"value":value},True)


def mongo_select(key):
	if(store_mongo):
		s = mongo_values.find_one({"key":key})
		if s:
			return s["value"]
		else:
			return ""

def helper_check_key(dic,key):
	if not key in dic:
		dic[key] = {}

def helper_mongo_store_keyvalue(group,key):
	global values
	helper_check_key(values,group)
	helper_check_key(values[group],key)
	mongo_update(group + "_" + key,	values[group][key])

def helper_mongo_restore_keyvalue(group,key):
	global values
	helper_check_key(values,group)
	helper_check_key(values[group],key)
	values[group][key]	= mongo_select(group + "_" + key)

def helper_car_mongo_to_value(auto,wert):
	global values
	val = mongo_select("auto"+str(auto)+str(wert))
	helper_check_key(values,"auto")
	helper_check_key(values["auto"],auto)
	helper_check_key(values["auto"][auto],wert)
	if(values["auto"][auto][wert] != val):
		values["auto"][auto][wert] = val
		return True
	else:
		return False

def store_keyvalues():
	global series,values
	if(exchange_store == "mongo"):
		# disk erstmal nicht
		helper_mongo_store_keyvalue("cpu","percent")
		helper_mongo_store_keyvalue("cpu","temperatur")
		helper_mongo_store_keyvalue("ram","total")
		helper_mongo_store_keyvalue("ram","used")
		helper_mongo_store_keyvalue("ram","percent")
	elif(exchange_store == "redis"):
		print_logger_error("redis not implemented")
	else:
		print_logger_error("no valid key value store")

def restore_keyvalues():
	global series,values
	if(exchange_store == "mongo"):
		helper_mongo_restore_keyvalue("cpu","percent")
		helper_mongo_restore_keyvalue("cpu","temperatur")
		helper_mongo_restore_keyvalue("ram","total")
		helper_mongo_restore_keyvalue("ram","used")
		helper_mongo_restore_keyvalue("ram","percent")
		
		# musik
		values["mpd"][1]			= mongo_select("mpd1")
		values["mpd"][2]			= mongo_select("mpd2")
		values["mpd"][3]			= mongo_select("mpd3")
	
		for r in range(auto_anzahl):
			for v in auto_sensoren:
				helper_car_mongo_to_value(r,v)
	elif(exchange_store == "redis"):
		print_logger_error("redis not implemented")
	else:
		print_logger_error("no valid key value store")

def read_1wire(wid):
	file = open('/sys/bus/w1/devices/' + wid + '/w1_slave')
	filecontent = file.read()
	file.close()
	stringvalue = filecontent.split("\n")[1].split(" ")[9]
	return float(stringvalue[2:]) / 1000

def log_1wire():
	print(str("28-011454989cff") + ' | %5.3f C' % read_1wire("28-011454989cff"))

def log_auto():
	global auto_sensoren
	for n in range(auto_anzahl):
		col = auto_sensoren[n]
		col.append("auto")
		val = []
		for v in auto_sensoren:
			val.append(values["auto"][n][v])
		val.append("auto"+str(n))
		points = {
				"name": "auto",
				"columns": col,
				"points": [val]
		}
		series.append(points)


def log_disk():
	global series,values
	partitions = psutil.disk_partitions()
	helper_check_key(values,"disk")
	for p in partitions:
		disk = psutil.disk_usage(p.mountpoint)
		points = {
			"name": "disk_usage",
			"columns": ["mount","used", "free", "percent", "host"],
			"points": [
				[p.mountpoint, disk.used, disk.free, disk.percent , hostname]
			]
		}
		series.append(points)
		helper_check_key(values["disk"],p.mountpoint)
		values["disk"][p.mountpoint]["used"] = disk.used
		values["disk"][p.mountpoint]["free"] = disk.free
		values["disk"][p.mountpoint]["percent"] = disk.percent
		print_logger("DISK -> " + p.mountpoint +  " :" + str(disk))

def log_cpu_temp():
	tstr = ""
	global series,values
	with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
		tstr = f.read()
	tfloat = float(tstr)
	tfloat = tfloat / 1000
	points = {
		"name": "cpu_temperatur",
		"columns": ["value", "host"],
		"points": [
			[tfloat, hostname]
		]
	}
	values["cpu"]["temperatur"] = tfloat
	print_logger("CPU -> temp:" + str(tfloat))
	series.append(points)

def log_cpu_percent():
	global series
	cpu = psutil.cpu_percent(interval=1)
	points = {
		"name": "cpu_percent",
		"columns": ["value", "host"],
		"points": [
			[cpu, hostname]
		]
	}
	values["cpu"]["percent"] = cpu
	series.append(points)
	print_logger("CPU -> percent:" + str(cpu))


def log_mem():
	global series
	mem = psutil.virtual_memory()
	points = {
			"name": "mem_usage",
			"columns": ["used", "total", "percent", "host"],
			"points": [
			[mem.used, mem.total, mem.percent, hostname]
			]
	}
	values["ram"]["used"] = mem.used
	values["ram"]["total"] = mem.total
	values["ram"]["percent"] = mem.percent
	series.append(points)
	print_logger("RAM -> used:" + str(mem.used/1024/1024) + "MB")


try:
	print colored("==========================================", 'red')
	print colored("AOR Logger Script running", 'magenta')
	print colored("Autor: ", 'magenta') + colored("David 'debauer' Bauer", 'white')
	print colored("==========================================", 'red')
	while(True):
		restore_keyvalues()
		log_cpu_percent()
		log_cpu_temp()
		log_mem()
		log_disk()
		log_1wire()
		influx_write_series()
		store_keyvalues()
		gc.collect()
		#time.sleep(1)

except (SystemExit):
	print " "
	print colored("SystemExit: stop script", "red")
	sys.exit()
except (KeyboardInterrupt):
	print " "
	print colored("KeyboardInterrupt: stop script", "red")
	sys.exit()


