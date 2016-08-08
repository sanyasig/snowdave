from BaseVoiceControllerModule import BaseVoiceControllerModule

from subprocess import Popen, PIPE, call

class SystemController(BaseVoiceControllerModule):
    def __init__(self):
       process = Popen(["pactl", "list", "sinks"], stdout=PIPE)
       # (output, err) = process.communicate()
       # exit_code = process.wait()
        #if not "bluez_sink.00_15_83_6B_63_41" in output:
       # if not "jongo" in output:
        #    print "Restarting mopidy"
         #   #call(["/home/pi/connectBluetoothAudio.sh"])
          #  call(["/home/pi/startPulse.sh"])
           # call(["sudo", "service", "mopidy", "restart"])

    def should_action(self, keyword, question):
        return "bluetooth" in question or "mopidy" in question or "pulseaudio" in question or "speaker" in question
        #return "enable" in question or "disable" in question or "turn on" in question or "turn off" in question or "connect" in question or "restart" in question

    def action(self, keyword, question):
        if "mopidy" in question:
            if "restart" in question:
                self.restart_mopidy()
        elif "bluetooth" in question:
            if "start" in question or "enable" in question or "on" in question:
                self.connect_bluetooth()
            elif "stop" in question or "disable" in question or "off" in question:
                self.disconnect_bluetooth()
        elif "pulseaudio" in question or "pulse" in question:
            if "restart" in question:
                self.restart_pulseaudio()

    def connect_bluetooth(self):
        call(["/home/pi/connectBluetoothAudio.sh"])

    def connect_pulseaudio(self):
        call(["/home/pi/startPulse.sh"])

    def restart_mopidy(self):
        #Stop and start rather than restart in case dead to begin with
        call(["sudo", "service", "mopidy", "stop"])

    def restart_pulseaudio(self):
        call(["/home/pi/startPulse.sh"])
        self.restart_mopidy()
