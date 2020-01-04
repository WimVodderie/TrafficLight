ln -s ~/services/trafficlight/trafficlight.service /etc/systemd/system/
systemctl enable trafficlight.service
systemctl start trafficlight.service
