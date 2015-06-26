** Influx DB **
https://github.com/eckardt/influxdb-backup.sh

install 
```
cd /home/pi
git clone https://github.com/stedolan/jq.git
cd jq
git checkout jq-1.4
autoreconf -i
./configure
make
make install
aptitude -y install curl

cd /home/aor/AOR2015/scripts
wget https://raw.githubusercontent.com/eckardt/influxdb-backup.sh/master/influxdb-backup.sh
chmod +x ./influxdb-backup.sh

```

usage
```
./influxdb-backup.sh dump aor2015 -u admin -p admin > ../backup/influx_dump01

```

** Influx DB **

```
mongodump -h localhost --port 3001 -d meteor
mongorestore -h localhost --port 3001 -d meteor dump/meteor
```