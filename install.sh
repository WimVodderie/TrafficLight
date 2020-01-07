ln -s $(pwd)/trafficlight.service /etc/systemd/system/
systemctl enable trafficlight.service
systemctl start trafficlight.service
