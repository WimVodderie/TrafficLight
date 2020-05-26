#!/bin/bash

# Write latest raspbian lite to sd card
#   windows: rufus
#   linux: balena etcher
echo "Warning: This expects a fresh install of buster lite. Run as root ( sudo ${0} )."

if [ 'root' != $( whoami ) ] ; then
  echo "Please run with sudo!"
  exit 1;
fi

# set timezone
rm /etc/localtime
sed -i "s?Europe/London?Europe/Brussels?" /etc/timezone
dpkg-reconfigure -f noninteractive tzdata

# enable ssh
ssh-keygen -A
update-rc.d ssh enable
invoke-rc.d ssh start

# change keyboard to us (default is gb)
sed -i /etc/default/keyboard -e "s/^XKBLAYOUT.*/XKBLAYOUT=\"us\"/"

# set date / time
echo -n "Enter current date-time (yyyy-mm-dd hh:mm): "
read TIMEDATE
date -s "$TIMEDATE"

# install some stuff
apt -y update
apt -y upgrade
apt -y install tmux git rpi.gpio python3-venv python3-pip lsof

# create mount point for udrive and add command to mount udrive to /etc/rc.local
mkdir -p /mnt/udrive
sed -i -e '$i # mount udrive (uid and gid are needed so that local user dfe can write to the share even when root mounted it)\nmount -t cifs //s00202/udrive /mnt/udrive -o user=dfe01,password=XBuilder,uid=$(id -u),gid=$(id -g)\n' /etc/rc.local

#
# deploy the Xeikon apps to /usr/local/xeikon
#
mkdir -p /usr/local/xeikon

# trafficlight
if [ ! -d /usr/local/xeikon/trafficlight ]; then
  pushd /usr/local/xeikon
  git clone https://github.com/WimVodderie/trafficlight
  cd trafficlight
  chmod +x install.sh
  . ./install.sh
  popd
fi

# doylestatus
if [ ! -d /usr/local/xeikon/DoyleStatus ]; then
  pushd /usr/local/xeikon
  git clone https://github.com/WimVodderie/DoyleStatus
  cd DoyleStatus
  python3 -m venv venv
  popd
fi

# get script to make the pi file system read-only
NOROOTUSER=$(who -m | awk '{print $1}')
echo "Non-root user: $NOROOTUSER"
if [ ! -d /home/$NOROOTUSER/rpi-readonly ]; then
  git clone http://gitlab.com/larsfp/rpi-readonly /home/$NOROOTUSER/rpi-readonly
fi

# set hostname - do this last
echo trafficlight > /etc/hostname
sed -i "s/127.0.1.1.*raspberry/127.0.1.1\ttrafficlight/g" /etc/hosts
