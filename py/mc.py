#!/usr/bin/python
#
#music and control daemon

import os,sys,time,serial,json,psutil,threading,argparse,aor
import RPi.GPIO as GPIO
<<<<<<< HEAD

import logging
import logging.handlers
import argparse

import aor.mpc as mpc

# Deafults
LOG_FILENAME = "/var/log/aor/mc.log"
LOG_LEVEL = logging.DEBUG  # Could be e.g. "DEBUG" or "WARNING"

parser = argparse.ArgumentParser(description="My simple Python service")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")
 
=======
import aor.mpc as MPC
from bson import BSON, json_util
from subprocess import *
from datetime import datetime
from termcolor import colored
import gaugette.rotary_encoder
from collections import deque
#import rrdtool
from adafruit.ADS1x15 import ADS as ADS1x15


parser = argparse.ArgumentParser(description="AOR 2015")
parser.add_argument("-n", "--nolog", help="no log, use stdio", default=False, action="store_true")
parser.add_argument("-v", "--values", help="show values", default=False, action="store_true")
parser.add_argument("-i", "--input", help="show input", default=False, action="store_true")
parser.add_argument("--only_sensor", help="only ", default=False, action="store_true")
parser.add_argument("--only_interface", help="only user Interface", default=False, action="store_true")
>>>>>>> 304b2489005a4f6ff9de417650125e4adb655888
args = parser.parse_args()

if not args.nolog:
	aor.stdio_logger.use_logging_handler(filename="/var/log/aor/mc.log",level="debug")

mode_data = False
mode_interface = False

if not args.only_interface and not args.only_sensor:
	mode_data = True
	mode_interface = True
	print "starte sensor und interface"
elif args.only_sensor:
	mode_data = True
	mode_interface = False
	print "starte nur sensor"
elif args.only_interface:
	mode_data = False
	mode_interface = True
	print "starte nur interface"

config = json.loads(open('/home/debauer/AOR2015/configs/aor_service.json').read())

playlist_lines = config['music']['playlist_lines']
hostname = config['hostname']
keyvalues = config['keyvalues']
w1 = config['w1']
circle_sleep = int(config['circle_sleep'])
telegram_sleep = float(config['telegram_sleep'])

keyvalue 	= aor.keyvalue.KeyValue(mongo=config['store']['mongo'],redis=config['store']['redis'])
if mode_data:
	log = aor.logger.Logger(rrd=config['store']['rrd'],influx=config['store']['influx'],influx_config=config['influx'])
	ADS1015 = 0x00  # 12-bit ADC
	ADS1115 = 0x01	# 16-bit ADC
	gain = 4096  # +/- 4.096V
	sps = 250
	adc = ADS1x15()

use_serial = False
if mode_interface:
	use_serial = True
	lcd_seite = 0
	lcd_seite_max = 3
	
	GPIO.setmode(GPIO.BOARD)
	#GPIO.setwarnings(False) 

	SERIAL_DATA = deque([])
	
	ENCODER_1 		= 33
	ENCODER_2 		= 35
	BUTTON_ENCODER  = 37
	BUTTON_NEXT		= 40
	BUTTON_PREV		= 38
	BUTTON_UP		= 22
	BUTTON_DOWN		= 18
	
	#GPIO.setup(ENCODER_1, 		GPIO.IN, pull_up_down = GPIO.PUD_UP)
	#GPIO.setup(ENCODER_2, 		GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(BUTTON_ENCODER, 	GPIO.IN, pull_up_down = GPIO.PUD_UP)
	GPIO.setup(BUTTON_NEXT, 	GPIO.IN, pull_up_down = GPIO.PUD_UP) 
	GPIO.setup(BUTTON_PREV,		GPIO.IN, pull_up_down = GPIO.PUD_UP) 
	GPIO.setup(BUTTON_UP, 		GPIO.IN, pull_up_down = GPIO.PUD_UP) 
	GPIO.setup(BUTTON_DOWN, 	GPIO.IN, pull_up_down = GPIO.PUD_UP) 


mpc = {}
series = []
data_log_hdd = ""
data_log_1w = ""
data_log_cpu = ""
data_log_ram = ""

def get_time():
	t = datetime.now()
	return t.strftime("%Y.%M.%d-%H:%M:%S")

start_time = get_time()

if(use_serial):
	ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
	time.sleep(1)

#def helper_car_mongo_to_value(auto,wert):
#	global values
#	val = keyvalue.select("auto"+str(auto)+str(wert))
#	helper_check_key(values,"auto")
#	helper_check_key(values["auto"],auto)
#	helper_check_key(values["auto"][auto],wert)
#	if(values["auto"][auto][wert] != val):
#		values["auto"][auto][wert] = val
#		return True
#	else:
#		return False

def get_time():
	t = datetime.now()
	return t.strftime("%Y.%M.%d-%H:%M:%S")

def check_file(path,file):
	if not (os.path.isfile(path + file)):
		return 0
	else:
		return 1

def write_dataset(file,data):
	with open("/home/debauer/data/" + file + "_" + start_time +  ".csv", "a") as f:
		f.write(data + "\n")

def log_analog():
	volts = adc.readADCSingleEnded(0, gain, sps) / 1000
	t = get_time()
	temp = 0.0
	points = {
		"name": "motor_ntc",
		"columns": ["volts", "tempertaur", "host"],
		"points": [
			[volts, temp, hostname]
		]
	}
	log.append_series(points)
	write_dataset("ntc",t+","+str(volts)+","+str(temp))

def read_1wire(wid):
	file = open('/sys/bus/w1/devices/' + wid + '/w1_slave')
	filecontent = file.read()
	file.close()
	stringvalue = filecontent.split("\n")[1].split(" ")[9]
	return float(stringvalue[2:]) / 1000

def log_1wire():
	global data_log_1w
	data = []
	t = get_time()
	for key,adr in w1.items():
		value = read_1wire(adr)
		points = {
				"name": "w1",
				"columns": [key],
				"points": [[value]]
		}
		if args.values:
			print(str(key) + ' | %5.3f C' % value)
		keyvalue.update("w1_"+key,value)
		data.append(str(value))
		log.append_series(points)
	data_str = ','.join(data)
	write_dataset("1wire",t+","+data_str)


def log_disk():
	global series, data_log_hdd
	partitions = psutil.disk_partitions()
	for p in partitions:
		disk = psutil.disk_usage(p.mountpoint)
		points = {
			"name": "disk_usage",
			"columns": ["mount","used", "free", "percent", "host"],
			"points": [
				[p.mountpoint, disk.used, disk.free, disk.percent , hostname]
			]
		}
		#keyvalue.update("hdd_",disk.used)
		#keyvalue.update("cpu_temperatur",disk.free)
		#keyvalue.update("cpu_temperatur",disk.percent)
		log.append_series(points)

def log_cpu():
	tstr = ""
	global series, data_log_cpu
	t = get_time()
	data = []
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
	cpu = psutil.cpu_percent(interval=1)
	points = {
		"name": "cpu_percent",
		"columns": ["value", "host"],
		"points": [
			[cpu, hostname]
		]
	}
	keyvalue.update("cpu_percent",cpu)
	log.append_series(points)
	keyvalue.update("cpu_temperatur",tfloat)
	log.append_series(points)
	write_dataset("cpu",t+","+str(tfloat)+","+str(cpu))


def log_mem():
	global series, data_log_ram
	mem = psutil.virtual_memory()
	t = get_time()
	points = {
			"name": "mem_usage",
			"columns": ["used", "total", "percent", "host"],
			"points": [
			[mem.used, mem.total, mem.percent, hostname]
			]
	}
	keyvalue.update("mem_used",mem.used)
	keyvalue.update("mem_total",mem.total)
	keyvalue.update("mem_percent",mem.percent)
	series.append(points)
	write_dataset("mem",t+","+str(mem.used)+","+str(mem.total)+","+str(mem.percent))

def serial_write(stri):
	global SERIAL_DATA
	#print "ON: " +  str
	#ser.write(str)
	SERIAL_DATA.append(stri)
	#else:
	#	print "OFF: " +  str


def send_mpd(id):
	global serial
	global mpc
	song = MPC.song()
	song_status = MPC.title_status()
	status = MPC.mpd_status()
	if(song != mpc["song"] or id == -2):
		mpc["song"] = song
		if(id == 0 or id < 0):
			serial_write("mpd 0 "+ mpc["song"] + " \r")
	if(song_status != mpc["song_status"] or id == -2):
		mpc["song_status"] = song_status
		if(id == 1 or id < 0):
			serial_write("mpd 1 "+ mpc["song_status"]["title"] + " \r")
	if(status != mpc["status"] or id == -2):
		if(id == 2 or id < 0):
			mpc["status"] = status
			serial_write("mpd 2 V: " + mpc["status"]["volume"] + "%  RE: " + mpc["status"]["repeat"] +"  RE: " + mpc["status"]["random"] +"\r")

# thread!
def thread_send_values():
	global serial
	value = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
	def value_string(i, value, old_value):
		time.sleep(0.2)
		val = keyvalue.select(value)
		if(val != old_value):
			serial_write("value "+ str(i) +" "+ "%5.1f" % val + " \r")
			return val
		return old_value
	while True:
		#time.sleep(0.2)
		try:
			value[0] = value_string(0,"w1_oel",			value[0])
			value[1] = value_string(1,"w1_bier",		value[1])
			value[2] = value_string(2,"cpu_temperatur",	value[2])
			value[3] = value_string(3,"w1_motor",		value[3])
			value[4] = value_string(4,"w1_aussen",		value[4])
			value[5] = value_string(5,"w1_innen",		value[5])
		except:
			print "thread_send_values: " + str(sys.exc_info())
			#return False

#thread
def thread_log_system():
	while True:
		time.sleep(1)
		try:
			log_cpu()
			log_mem()
			log_disk()
			log_analog()
		except:
			print "thread_log_system: " + str(sys.exc_info())
			return False

def thread_log_1wire():
	while True:
		try:
			log_1wire()
		except:
			print "thread_log_1wire: " + str(sys.exc_info())
			return False

def cleanup():
	if(use_serial):
		ser.close()
	GPIO.cleanup()


def event_up(channel):
	if(lcd_seite == lcd_seite_max):
		lcd_seite = 0
	else:
		lcd_seite = lcd_seite + 1
	if args.input:
		print "Taste: UP - Seite: " + lcd_seite 

def event_down(channel):
	if(lcd_seite == 0):
		lcd_seite = lcd_seite_max
	else:
		lcd_seite = lcd_seite - 1
	if args.input:
		print "Taste: DOWN - Seite: " + lcd_seite 

def event_next(channel):
	if args.input:
		print "Taste: NEXT - mpc next"
	MPC.next()


def event_prev(channel):
	if args.input:
		print "Taste: PREV - mpc prev"
	MPC.prev()

def event_encoder(channel):
	if args.input:
		print "Taste: ENCODER - mpc toggle"
	#if(lcd_seite == )
	MPC.toggle()

def thread_rotary():
	encoder = gaugette.rotary_encoder.RotaryEncoder(23, 24)
	while True:
		#time.sleep(0.5)
		#print "rotary thread"
		delta = encoder.get_delta()
		if delta!=0:
			MPC.setvolume(delta)
			#print "rotate %d" % delta

def thread_log_series():
	while 1:
		try:
			time.sleep(5)
			log.write_series()
		except:
			print "thread_log_series: " + str(sys.exc_info())

def thread_adc():
	global ser, use_serial
	if(use_serial):
		while True:
			sys.stdout.write(ser.read(1))

def thread_mpc():
	global serial
	global mpc
	old_song = ""
	old_song_status = ""
	old_status = {}
	while 1:
		try:
			time.sleep(1)
			song = MPC.song()
			song_status = MPC.title_status()
			status = MPC.mpd_status()
			if(song != old_song):
				old_song = song
				serial_write("mpd 0 "+ old_song[:23] + " \r")
			if(song_status != old_song_status):
				old_song_status = song_status
				serial_write("mpd 1 "+ old_song_status + " \r")
			if(status != old_status):
				old_status = status
				serial_write("mpd 2 " + old_status +"\r")
		except:
			print "thread_mpc: " + str(sys.exc_info())


if mode_interface:
	GPIO.add_event_detect(BUTTON_NEXT, 		GPIO.FALLING, callback=event_next, 		bouncetime=300)
	GPIO.add_event_detect(BUTTON_PREV, 		GPIO.FALLING, callback=event_prev, 		bouncetime=300)
	GPIO.add_event_detect(BUTTON_UP, 		GPIO.FALLING, callback=event_up, 		bouncetime=300)
	GPIO.add_event_detect(BUTTON_DOWN, 		GPIO.FALLING, callback=event_down, 		bouncetime=300)
	GPIO.add_event_detect(BUTTON_ENCODER, 	GPIO.FALLING, callback=event_encoder, 	bouncetime=300)

if mode_data:
	thLogAdc 	= threading.Thread(target=thread_adc)
	thLogSystem = threading.Thread(target=thread_log_system)
	thLog1Wire 	= threading.Thread(target=thread_log_1wire)
	thLogSeries = threading.Thread(target=thread_log_series)
	thLogAdc.daemon = True
	thLogSystem.daemon = True
	thLog1Wire.daemon = True
	thLogSeries.daemon = True
	

if mode_interface:
	thValues 	= threading.Thread(target=thread_send_values)
	thEncoder 	= threading.Thread(target=thread_rotary)
	thMPCWorker = threading.Thread(target=MPC.worker)
	thMPC 		= threading.Thread(target=thread_mpc)
	thEncoder.daemon = True
	thMPCWorker.daemon = True
	thMPC.daemon = True
	thValues.daemon = True

try:
	if mode_interface:
		MPC.connect()
		thMPC.start()
		thEncoder.start()
		thMPCWorker.start()	
		thValues.start()

	if mode_data:
		thLogSystem.start()
		thLog1Wire.start()
		thLogSeries.start()
		thLogAdc.start()

	print "start main loop"
	if mode_interface:
		while True:
			time.sleep(0.1)
			try:
				ds = SERIAL_DATA.popleft()
				print "serial:" +  ds
				ser.write(ds)
			except IndexError:
				pass
				#print "dafuq"
	else:
		while True:
			pass
except KeyboardInterrupt:
	print "KeyboardInterrupt"	
except:
	print sys.exc_info()
	print "other error"	
finally:
	#thValues.terminate()
	#thLogSystem.terminate()
	#thLog1Wire.terminate()
	cleanup()
