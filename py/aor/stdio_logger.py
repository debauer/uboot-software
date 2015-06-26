import os,sys
import logging
import logging.handlers

class MyLogger(object):
	def __init__(self, logger, level):
		"""Needs a logger and a logger level."""
		self.logger = logger
		self.level = level
	 
	def write(self, message):
		# Only log if there is a message (not just a new line)
		if message.rstrip() != "":
			self.logger.log(self.level, message.rstrip())

def use_logging_handler(filename,level):
	if(level == "debug"):
		LOG_LEVEL = logging.DEBUG
	elif(level == "warning"):
		LOG_LEVEL = logging.WARNING 
	else:
		LOG_LEVEL = logging.DEBUG 
	logger = logging.getLogger(__name__)
	logger.setLevel(LOG_LEVEL)
	handler = logging.handlers.TimedRotatingFileHandler(filename, when="midnight", backupCount=3)
	formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	
	 
	# Replace stdout with logging to file at INFO level
	sys.stdout = MyLogger(logger, logging.INFO)
	# Replace stderr with logging to file at ERROR level
	sys.stderr = MyLogger(logger, logging.ERROR)