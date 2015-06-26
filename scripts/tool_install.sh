
# elasticsearch 1.4.4 - tested on rpi2 - wird erstmal nicht mehr gebraucht

#	mkdir /usr/share/elasticsearch
#	cd /usr/share/elasticsearch
#	curl -L -O https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.4.tar.gz
#	
#	echo "path.data: /mnt/ssd0/elasticdata" > config/elasticsearch.yml
#	
#	#mv elasticsearch-1.4.4 elasticsearch
#	cd bin
#	./elasticsearch -d 
#	echo "@reboot /usr/share/elasticsearch/bin/elasticsearch -d" > /etc/crontab

# mongodb 2.1.1 - tested on rpi2
# https://github.com/RickP/mongopi
	cd /home/pi
	git clone https://github.com/svvitale/mongo4pi
	cd mongo4pi
	./install.sh

# nodejs v0.10.37 - tested on rpi2
	curl -sL https://deb.nodesource.com/setup | sudo bash -
	aptitude -y install build-essential python-dev python-rpi.gpio nodejs

# apache 2
	aptitude -y install apache2

# graphite - verworfen
#	cd /home/aor/AOR2015/py
#	pip install -r requirements.txt
#	cd /opt/graphite/conf/
#   ... 
  
# mpd

	aptitude -y install mpd mpc ncmpc
	#default: music_directory         "/var/lib/mpd/music"
	cp /home/aor/AOR2015/configs/mpd.conf /etc/mpd.conf
	#sed -i 's!dir = .*!music_directory "/mnt"!g' /etc/mpd.conf  #funzt ned :/



# influxdb
	cd /home/pi
	wget http://demos.pihomeserver.fr/influxdb_0.8.6_armhf.deb
	dpkg --install influxdb_0.8.6_armhf.deb

	sed -i 's!dir = .*!dir = "/mnt/ssd0/data_influx/db"!g' /opt/influxdb/shared/config.toml
	service influxdb start

# grafana
	cd /var/www
	wget http://grafanarel.s3.amazonaws.com/grafana-1.9.1.tar.gz
	tar -xzf grafana-1.9.1.tar.gz grafana-1.9.1
	mv grafana-1.9.1 grafana
	cd grafana
	cat /home/aor/AOR2015/configs/grafana.js >> config.js

# misc
	aptitude -y install rrdtool python-rrdtool


# aor_daemon
	cd /home/aor/AOR2015/py
	pip install -r requirements.txt
	echo "deamon fehlt noch. muss per hand gestartet werden."
	echo "run as aor: /home/aor/AOR2015/py/./rest_daemon.py"
