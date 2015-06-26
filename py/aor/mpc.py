from subprocess import *
<<<<<<< HEAD

def cmd(cmd):
	p = Popen('mpc ' +, shell=True, stdout=PIPE)
=======
from threading import Lock, Thread
from random import choice
from mpd import MPDClient
import time

class LockableMPDClient(MPDClient):
	def __init__(self, use_unicode=False):
		super(LockableMPDClient, self).__init__()
		self.use_unicode = use_unicode
		self._lock = Lock()
	def acquire(self):
		self._lock.acquire()
	def release(self):
		self._lock.release()
	def __enter__(self):
		self.acquire()
	def __exit__(self, type, value, traceback):
		self.release()

client = LockableMPDClient()
var_album = ""
var_artist = ""
var_title = ""
var_trackNr = ""
var_trackTime = ""
var_volume = 30
var_state  = ""
var_repeat = ""
var_random = ""

def connect():
	#client = MPDClient()               # create client object
	client.timeout = 10                # network timeout in seconds (floats allowed), default: None
	#client.idletimeout = None          # timeout for fetching the result of the idle command is handled seperately, default: None
	client.connect("192.168.1.6", 6600)  # connect to localhost:6600
	print(client.mpd_version)          # print the MPD version
	#print(client.find("any", "house")) # print result of the command "find any house"

def disconnect():
	client.close()                     # send the close command
	client.disconnect()                # disconnect from the server

def worker():
	global var_title , var_album , var_artist , var_trackNr, var_trackTim, var_state , var_repeat, var_random	
	#{'album': 'The Mindsweep', 'artist': 'Enter Shikari', 'track': '5/13', 
	#'title': 'Never Let Go Of The Microscope', 'albumartist': 'Enter Shikari', 
	#'pos': '5', 'last-modified': '2015-01-13T01:49:57Z', 'disc': '1/1', 'file': 
	#'ssd0/musik/Enter Shikari - The Mindsweep (2015) [320]/05 Never Let Go Of The Microscope.mp3', 
	#'time': '243', 'date': '2015', 'genre': 'Alternative', 'id': '5'}

	#{'songid': '5', 'playlistlength': '14', 'playlist': '2', 'repeat': '1', 'consume': '0', 
	#'mixrampdb': '0.000000', 'random': '0', 'state': 'play', 'xfade': '0', 'volume': '4', 'single': '0', 
	#'mixrampdelay': 'nan', 'nextsong': '6', 'time': '60:243', 'song': '5', 'elapsed': '59.617', 'bitrate': '320', 
	#'nextsongid': '6', 'audio': '44100:24:2'}

	while True:
		time.sleep(0.1)
		with client:
			client.setvol(var_volume)
		with client: # acquire lock
			status = client.status()
			song = client.currentsong()
		try:
			var_title 		= song["title"]
			var_album 		= song["album"]
			var_artist 		= song["artist"]
			var_trackNr 	= song["track"]
		except:
			var_title 		= " "
			var_album 		= " "
			var_artist 		= "md3 error"
			var_trackNr 	= "x"			

		try:
			var_trackTime 	= status["time"]
			var_state 		= status["state"]
			#var_volume		= status["volume"]
			var_repeat		= status["repeat"]
			var_random		= status["random"]
		except:
			var_trackTime 	= "xxx"
			var_state 		= "xx"
			#var_volume		= status["volume"]
			var_repeat		= "x"
			var_random		= "x"

def cmd(cmd):
	p = Popen('mpc ' + cmd, shell=True, stdout=PIPE)
>>>>>>> 304b2489005a4f6ff9de417650125e4adb655888
	output = p.communicate()[0]
	return output

def stats():
	s =  cmd('stats')
	l = s.split('\n')
	return {"artists": int(l[0][8:]),
			"albums": int(l[1][7:]),
			"songs": int(l[2][6:]),
			"play_time": l[4][10:],
			"uptime": l[5][7:],
			"db_updated": l[6][11:],
			"db_play_time": l[7][13:]
		}

<<<<<<< HEAD
def song():
	return cmd('mpc current')

def title_status():
	s =  cmd('')
	if(s[0:6] != "volume"):
		a = s.split('\n')
		d = a[1]
	else:
		d = ""
	status = {}
	if(d!=""):
		status["position"] = d[11:16] 
		status["time"] = d[19:28]
		if(d[:9] == "[paused]"):
			status["title"] = d[10:]
		elif(d[:9] == "[playing]"):
			status["title"] = d[11:]
		else:
			status["title"] = " "
	else:
		status["title"] = " "
		status["position"] = "asd" 
		status["time"] = "00:00:00"
	#print status["title"]
	return status

def mpd_status():
	s =  cmd('')
	if(s[0:6] != "volume"):
		a = s.split('\n')
		l = a[2]
	else:
		l = s
	status = {"volume": l[7:10],"repeat": l[22:25],"random": l[36:39],"single": l[50:53],"consume": l[65:68],"position": "xx/xx","title": ""}
 	return status

def playlist(inc,length = 4):
	p =  mpc_cmd('playlist')
=======
def trackNr():
	return var_trackNr

def trackTime():
	return var_trackTime

def song():
	return var_artist + " - " + var_title

def state ():
	return var_state
def volume():
	return var_volume
def repeat():
	return var_repeat
def random():
	return var_random

def title_status():
	return "Nr: " + var_trackNr +  " Time: " + var_trackTime[:4]

def mpd_status():
	return "V: " + str(var_volume) +  "%  RA: " + str(var_random) +"  RE: " + str(var_repeat)

def playlist(inc,length = 4):
	p =  cmd('playlist')
>>>>>>> 304b2489005a4f6ff9de417650125e4adb655888
	playlist = p.split('\n')
	partlist = []
	if(inc>=len(playlist)):
		inc = 0
	if(len(playlist)> inc+length):
		for i in range(inc,inc+length):
			partlist.append(playlist[i])
	else:
		for i in range(inc,len(playlist)):
			partlist.append(playlist[i])
		#print inc+length-len(playlist)
		for i in range(inc+length-len(playlist)+1):
			partlist.append(playlist[i])
<<<<<<< HEAD
	return partlist
=======
	return partlist


def next():
	with client:
		client.next()

def prev():
	with client:
		client.previous()

def setvolume(vol):
	global var_volume
	var_volume = var_volume + int(vol)
	if (var_volume > 100):
		var_volume = 100
	if (var_volume < 0):
		var_volume = 0
	print var_volume

def toggle():
	with client:
		client.pause()
>>>>>>> 304b2489005a4f6ff9de417650125e4adb655888
