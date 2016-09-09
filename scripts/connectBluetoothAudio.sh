#!/bin/bash
echo -e 'connect 00:15:83:6B:63:41\nquit' | bluetoothctl
sleep 6

#new_sink=$(pacmd list-sinks | grep index | tee /dev/stdout | grep -m1 -A1 "* index" | tail -1 | cut -c12-)
#pactl set-default-sink $new_sink

#pactl set-default-sink bluez_sink.00_15_83_6B_63_41
#sudo service mopidy restart

#Disable HDMI to save power
#/usr/bin/tvservice -o

#Disable the wifi
#sudo iwconfig wlan0 txpower off
