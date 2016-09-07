from BaseVoiceControllerModule import BaseVoiceControllerModule

from subprocess import Popen, PIPE, call
import subprocess
import socket
import struct
import os

class SystemController(BaseVoiceControllerModule):
    def __init__(self):
        if os.name != "nt":
            process = Popen(["pactl", "list", "short", "sinks"], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            #if not "bluez_sink.00_15_83_6B_63_41" in output:
            if not "jongo" in output:
                print("Couldn't find jongo in pulse audio's sink selection, will fire up pulse audio and then restart mopidy")
                print output
                #call(["/home/pi/connectBluetoothAudio.sh"])
                call(["/home/pi/startPulse.sh"])
                #call(["sudo", "service", "mopidy", "restart"])

    def should_action(self, witai, question):
        return "bluetooth" in question or "mopidy" in question or "pulseaudio" in question or "speaker" in question or "pc" in question or "emulation" in question
        #return "enable" in question or "disable" in question or "turn on" in question or "turn off" in question or "connect" in question or "restart" in question

    def action(self, witai, question, audio):
        intent = self.get_witai_item(witai, "intent")
        action = self.get_witai_item(witai, "action")
        search_query = self.get_witai_item(witai, "search_query")

        if "pc" in intent:
            if "shutdown" in action:
                self.response.say("Shutting down Ash's PC")
                self.shutdown_windows_on_lan(self.config["pc"]["host"], self.config["pc"]["user"])
            else:
                self.response.say("Waking Ash's PC")
                self.wake_on_lan(self.config["pc"]["mac"])
        elif "speaker" in intent:
            chosenSpeaker = self.config["speakers"]["default"]
            for option in self.config["speakers"]:
                if (search_query and option in search_query) or (not search_query and option in question):
                    chosenSpeaker = self.config["speakers"][option]
                    break
            self.change_speaker(chosenSpeaker)
        elif "emulation" in intent:
            if self.contains_stop_word(action):
                self.stop_emulationstation()
            else:
                self.start_emulationstation()
        elif "mopidy" in intent:
            if "restart" in action:
                self.restart_mopidy()
        elif "bluetooth" in intent:
            if self.contains_stop_word(action):
                self.disconnect_bluetooth()
            else:
                self.connect_bluetooth()
        elif "pulseaudio" in question or "pulse" in question:
            if "restart" in question:
                self.restart_pulseaudio()

    def start_emulationstation(self):
        CREATE_NEW_CONSOLE = 0x00000010
        pid = subprocess.Popen(["emulationstation"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).pid # , creationflags=CREATE_NEW_CONSOLE (windows)

    def stop_emulationstation(self):
        subprocess.Popen(["pkill", "-f", "emulationstation"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

    def connect_bluetooth(self):
        process = Popen(["/home/pi/connectBluetoothAudio.sh"], stdout=PIPE)
        process.wait()
        self.change_speaker(self.config["bluetooth"]["default"])

    def connect_pulseaudio(self):
        call(["/home/pi/startPulse.sh"])

    def restart_mopidy(self):
        #Stop and start rather than restart in case dead to begin with
        call(["sudo", "service", "mopidy", "stop"])
        call(["sudo", "service", "mopidy", "start"])

    def restart_pulseaudio(self):
        call(["/home/pi/startPulse.sh"])
        self.restart_mopidy()

    def change_speaker(self, sinkName):
        call(["/home/pi/moveSink.sh", sinkName])

    def wake_on_lan(self, macaddress):
        """ Switches on remote computers using WOL. """

        # Check macaddress format and try to compensate.
        if len(macaddress) == 12:
            pass
        elif len(macaddress) == 12 + 5:
            sep = macaddress[2]
            macaddress = macaddress.replace(sep, '')
        else:
            raise ValueError('Incorrect MAC address format')
     
        # Pad the synchronization stream.
        data = ''.join(['FFFFFFFFFFFF', macaddress * 20])
        send_data = '' 

        # Split up the hex values and pack.
        for i in range(0, len(data), 2):
            send_data = ''.join([send_data,
                                 struct.pack('B', int(data[i: i + 2], 16))])

        # Broadcast it to the LAN.
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(send_data, ('<broadcast>', 7))

    def shutdown_windows_on_lan(self, host, user):
        #call(["net", "rpc", "shutdown", "-I", host, "-U", user+"%"+windows_password])
        call(["ssh", "-l", user, host, "shutdown", "/h"])
