import sys
import pyttsx
import signal
import pyaudio
#from pydub import AudioSegment
import speech_recognition as sr

from subprocess import Popen, PIPE, call

import modules
from modules import *
from lib import snowboydecoder

class VoiceController:
    MODEL = "lib/resources/Alexa.pmdl"
    SENSITIVITY = 0.5
    INTERRUPTED = False
    
    def __init__(self):
        self.create_detector()
        self.pyttsx_engine = pyttsx.init()
        voices = self.pyttsx_engine.getProperty('voices')
        if len(voices) > 1:
            self.pyttsx_engine.setProperty('voice', voices[0].id)

        self.modules = []
        for module in modules.__all__:
            print "Loading module: " + module
            self.modules.append(eval(module + "." + module + "()"))

    def create_detector(self):
        self.detector = snowboydecoder.HotwordDetector(self.MODEL, resource="lib/resources/common.res", sensitivity=self.SENSITIVITY)
	self.detector.start(detected_callback=self.listen_for_job, interrupt_check=self.interrupt_callback, sleep_time=0.03)
    def signal_handler(self, signal, frame):
        self.INTERRUPTED = True

    def interrupt_callback(self):
        return self.INTERRUPTED

    def main(self):
        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        while not self.INTERRUPTED:
            print "Listening for hotword..."
            self.detector.start(detected_callback=self.listen_for_job, interrupt_check=self.interrupt_callback, sleep_time=0.03)
        self.detector.terminate()

    def listen_for_job(self):
        self.detector.terminate()
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print "Listening for main question..."
            self.ding_sound()
            audio = r.listen(source)
            snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)
        try:
            print "Sending voice to Google"
            question = r.recognize_google(audio).lower()
            print("Google thinks you said: " + question)
            self.process_job(question)
        except sr.UnknownValueError:
            print("There was a problem whilst processing your question")
        self.create_detector()

    def talk_back(self, text_to_say):
        self.pyttsx_engine.say(text_to_say)
        self.pyttsx_engine.runAndWait()

    def ding_sound(self):
        #audioStream = AudioSegment.from_wav("resources/ding.wav")
        #play(audioStream)
        snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
        #snowboydecoder.play_audio_file(snowboydecoder.DETECT_DONG)

    def process_job(self, question):
	print "pricess question :" + question
        #for module in self.modules:
         #   if module.should_action(None, question):
          #      module.action(None, question)
           #     # Potentially don't break here, depends if multiple modules should action something or not?
            #    break



if __name__ == "__main__":
    vc = VoiceController()
    vc.main()
    #vc.process_job("play me some music")
