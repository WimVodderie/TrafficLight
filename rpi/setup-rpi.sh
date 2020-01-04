#!/bin/bash

# Write latest raspbian lite to sd card
#   windows: rufus
#   linux: balena etcher
echo "Warning: This expects a fresh install of buster lite. Run as root ( sudo ${0} )."

if [ 'root' != $( whoami ) ] ; then
  echo "Please run as root!"
  exit 1;
fi

# set timezone
echo Europe/Brussels > /etc/timezone

# set hostname
echo trafficlight > /etc/hostname

# enable ssh
ssh-keygen -A
update-rc.d ssh enable
invoke-rc.d ssh start

# change keyboard to us (default is gb)
sed -i /etc/default/keyboard -e "s/^XKBLAYOUT.*/XKBLAYOUT=\"us\"/"

# set date / time
echo -n "Enter current date-time (yyyy-mm-dd hh:mm): "
read TIMEDATE
date -s $TIMEDATE

# install some stuff
apt update
apt upgrade
atp install tmux git rpi.gpio python3-venv lsof

# download and install trafficlight service
mkdir -p ~/services
cd ~/services
git clone https://github.com/WimVodderie/trafficlight
chmod +x install.sh
. ./install.sh

# download DoyleStatus
mkdir -p ~/services
cd ~/services
git clone https://github.com/WimVodderie/DoyleStatus
cd DoyleStatus
python3 -m venv venv

# create mount point for udrive and add command to mount udrive to /etc/rc.local
mkdir -p /mnt/udrive
sed -i -e '$i # mount udrive (uid and gid are needed so that local user dfe can write to the share
even when root mounted it)\nmount -t cifs //s00202/udrive /mnt/udrive -o user=dfe01,password=XBuilder,uid=$(id -u),gid=$(id -g)\n' /etc/r
c.local

# get script to make the pi file system read-only
cd ~
git clone http://gitlab.com/larsfp/rpi-readonly
