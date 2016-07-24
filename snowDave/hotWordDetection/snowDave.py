import os
import signal

import snowboydecoder
from voiceDetection.voiceProcessor import VoiceProcessor


class SnowDave():

    global interrupted

    def  __init__(self):
        self.interrupted = False
        self.model = os.path.dirname(os.path.realpath(__file__)) + "/Alexa.pmdl"


    def signal_handler(self,signal, frame):
        self.interrupted = True

    def interrupt_callback(self):
        return self.interrupted

    #vr.askQuestion("turn on tv")

    def startSnowDave(self):
        vr = VoiceProcessor()
        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)

        detector = snowboydecoder.HotwordDetector(self.model, sensitivity=0.40)
        print('Listening... Press Ctrl+C to exit')

        # main loop
        detector.start(detected_callback=vr.getQuestion,
                       interrupt_check=self.interrupt_callback,
                       sleep_time=0.03)

        detector.terminate()
