from BaseVoiceControllerModule import BaseVoiceControllerModule

from subprocess import Popen, PIPE, call

class SystemController(BaseVoiceControllerModule):
    def __init__(self):
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

    def should_action(self, keyword, question):
        return "bluetooth" in question or "mopidy" in question or "pulseaudio" in question or "speaker" in question
        #return "enable" in question or "disable" in question or "turn on" in question or "turn off" in question or "connect" in question or "restart" in question

    def action(self, keyword, question):
        if "speaker" in question:
            if "bathroom" in question:
                self.change_speaker("jongos3bathroom_dlna")
            elif "kitchen" in question:
                self.change_speaker("jongos3kitchen_dlna")
            elif "bedroom" in question:
                self.change_speaker("jongos3bedroom_dlna")
            elif "house" in question:
                self.change_speaker("bluez_sink.00_15_83_6B_63_41")
            else:
                self.change_speaker("jongos3playroom_dlna")
        elif "mopidy" in question:
            if "restart" in question:
                self.restart_mopidy()
        elif "bluetooth" in question:
            if "disconnect" in question or "stop" in question or "disable" in question or "off" in question:
                self.disconnect_bluetooth()
            elif "connect" in question or "start" in question or "enable" in question or "on" in question:
                self.connect_bluetooth()
        elif "pulseaudio" in question or "pulse" in question:
            if "restart" in question:
                self.restart_pulseaudio()

    def connect_bluetooth(self):
        process = Popen(["/home/pi/connectBluetoothAudio.sh"], stdout=PIPE)
        process.wait()
        self.change_speaker("bluez_sink.00_15_83_6B_63_41")

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
