Installations Anleitung für den RPI2
=======

Erstmal den aor User anlegen und dieses Git Repo clonen
```
root@raspberrypi / # adduser aor
root@raspberrypi / # cd /home/aor
root@raspberrypi /home/aor # git clone https://github.com/debauer/AOR2015
root@raspberrypi /home/aor # chown aor:aor * -R
```

dann den ersten install script ausführen
```
root@raspberrypi /home/aor # cd AOR2015
root@raspberrypi /home/aor/AOR2015 # ./scripts/basic_install.sh
```

Der Raspi startet danach erstmal neu.
Dann kanns an den 2ten script gehen. Dieser installiert alle benötigten Programme.
```
root@raspberrypi / # cd /home/aorAOR2015
root@raspberrypi /home/aor/AOR2015 # ./scripts/tool_install.sh
```

Im besten Fall sollte der Raspi nun eingerichtet sein.