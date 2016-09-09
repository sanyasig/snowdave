#!/bin/sh

if [ 0 -eq "$1" ]
then
    pkill -f voicecontroller
    /usr/bin/tvservice -o
    sudo iwconfig wlan0 txpower off
    sudo /etc/init.d/networking stop
    sudo sh -c "echo 0 > /sys/devices/platform/soc/3f980000.usb/buspower"
    pkill -f pulse
else
    sudo /etc/init.d/networking start
    sudo sh -c "echo 1 > /sys/devices/platform/soc/3f980000.usb/buspower"
    sleep 6
    /usr/bin/tvservice -p
    /home/pi/startPulse.sh
    pactl set-default-sink alsa_output.usb-0d8c_USB_Sound_Device-00-Device.analog-stereo
    pactl set-default-source alsa_input.usb-OmniVision_Technologies__Inc._USB_Camera-B4.09.24.1-01-CameraB409241.analog-4-channel-input
    cd /opt/snowdave/; pkill -f voicecontroller; nohup python voicecontroller.py noready &
fi
