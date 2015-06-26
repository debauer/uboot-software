from subprocess import *
from influxdb.influxdb08 import InfluxDBClient
from influxdb.influxdb08.client import InfluxDBClientError
import rrdtool,sys
from termcolor import colored


class Logger(object):
	store_influx = False
	store_rrd = False
	influx_db = {}
	series = []
	log_info = True;
	log_error = True;

	def __init__(self, influx_config, rrd = False, influx = True, log_error = True, log_info = True):
		self.store_influx = influx
		if(self.store_influx):
			self.influx_db = InfluxDBClient(influx_config['host'],influx_config['port'],influx_config['user'],influx_config['pw'],influx_config['db'])

		#if(self.store_rrd):
	
	def append_series(self, data):
		self.series.append(data)

	def write_series(self):
		if(self.store_influx):
			#print "write_series"
			try:
				if(self.series != []):
					self.influx_db.write_points(self.series)
					self.series = []
			except InfluxDBClientError:
				print sys.exc_info()
				self.influx_ClientError()
			except requests.exceptions.ConnectionError:
				print sys.exc_info()
				self.influx_ConnectionError()
		else:
			self.series = []


	def log(self, str):
		if(self.log_info):
			print colored("logger:", 'cyan'), colored(str, 'magenta')

	def log_error(self, str):
		if(self.log_error):
			print colored("error:", 'red'), colored(str, 'magenta')
	
	def influx_ConnectionError(self):
		self.log_error("INFLUX ConnectionError")
	
	def influx_ClientError(self):
		self.log_error("INFLUX ClientError")