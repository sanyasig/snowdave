#!/bin/sh
sudo iwconfig wlan0 txpower off


ps -ef | grep Xvfb | grep -v grep > /dev/null
if [ $? -ne 0 ]; then
	echo Starting Xvfb
	Xvfb :1 -screen 0 1x1x8 &
	sleep 10
        pkill -f pulseaudio
fi

ps -ef | grep dbus-launch | grep -v grep > /dev/null
if [ $? -ne 0 ]; then
	echo Starting DBus
	DISPLAY=:1 dbus-launch
	sleep 1
fi
ps -ef | grep pulseaudio | grep -v grep > /dev/null
if [ $? -ne 0 ]; then
	echo Starting PulseAudio 
	DISPLAY=:1 pulseaudio --disallow-exit --disable-shm --exit-idle-time=-1 --start
	sleep 3
fi
ps -ef | grep pulseaudio-dlna | grep -v grep > /dev/null
if [ $? -ne 0 ]; then
	echo Starting PulseAudio-DLNA
	#DISPLAY=:1 pulseaudio-dlna --disable-workarounds &
	DISPLAY=:1 pulseaudio-dlna --disable-switchback --auto-reconnect --port 8085 &
	#while true; do
	#	sleep 60;
	#done;
	echo Restarting Mopidy
	sudo service mopidy restart
	sleep 10
fi
#pactl set-default-sink jongos3playroom_dlna
#pacmd load-module module-combine-sink sink_name=combined slaves=jongos3bedroom_dlna,jongos3playroom_dlna,jongos3kitchen_dlna,jongos3bathroom_dlna

pactl set-default-sink alsa_output.usb-0d8c_USB_Sound_Device-00-Device.analog-stereo
pactl set-default-source alsa_input.usb-OmniVision_Technologies__Inc._USB_Camera-B4.09.24.1-01-CameraB409241.analog-4-channel-input

#Disable HDMI to save power
#/usr/bin/tvservice -o
