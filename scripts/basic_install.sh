# sd card expanden ned vergessen!

# basic
	sudo aptitude update
	sudo aptitude upgrade
	sudo su
	cd 
	cat /home/pi/.bashrc >> .bashrc
	aptitude -y install htop screen mc python-pip
	adduser --disabled-password --gecos "" aor 

# USB fix
	echo "max_usb_current=1" >> /boot/config.txt

# samba
	aptitude -y install samba samba-common-bin

	echo "security = user" > nano /etc/samba/smb.conf
	sed -i 's/#security = user/security = user/g' /etc/samba/smb.conf
	echo "[aor]" > /etc/samba/smb.conf
	echo "path = /home/aor" > /etc/samba/smb.conf
	echo "writeable = yes" > /etc/samba/smb.conf
	echo "guest ok  = no" > /etc/samba/smb.conf

# rebooooten
	reboot