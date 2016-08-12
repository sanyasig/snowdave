import pyttsx
import signal
#from pydub import AudioSegment
import speech_recognition as sr
import logging
import os

import modules
from modules import *
from lib import snowboydecoder

from gtts import gTTS
import pyglet
from tempfile import NamedTemporaryFile
import subprocess

class ResponseLibrary:
    ENGINE = "google" #"pyttsx"
    def __init__(self):
        self.pyttsx_engine = pyttsx.init()
        voices = self.pyttsx_engine.getProperty('voices')
        if os.name == "nt" and len(voices) > 1:
            self.pyttsx_engine.setProperty('voice', voices[0].id)



    def say(self, message):
        logging.info(message)
        print(message)
        if self.ENGINE == "google":
            tts = gTTS(text=message, lang='en')
            f = NamedTemporaryFile(suffix=".mp3")
            tts.write_to_fp(f)
            f.flush()
            subprocess.Popen(['mpg123', '-q', f.name]).wait()
            f.close()

            #music = pyglet.media.load(f.name)
            #music.play()
            #pyglet.app.run()
        else:
            self.pyttsx_engine.say(message)
            self.pyttsx_engine.runAndWait()

    def ding(self, dong=False):
        sound = snowboydecoder.DETECT_DONG if dong else snowboydecoder.DETECT_DING
        snowboydecoder.play_audio_file(sound)

class VoiceController:
    MODEL = "lib/resources/Alexa.pmdl"
    SENSITIVITY = 0.5
    INTERRUPTED = False
    FINISHED_PROCESSING_JOB = True
    
    def __init__(self):
        self.create_detector()
        self.response_library = ResponseLibrary()

        self.modules = []
        for module in modules.__all__:
            logging.info("Loading module: " + module)
            moduleInstance = eval(module + "." + module + "()")
            moduleInstance.set_response_library(self.response_library)
            self.modules.append(moduleInstance)

    def create_detector(self):
        self.detector = snowboydecoder.HotwordDetector(self.MODEL, resource="lib/resources/common.res", sensitivity=self.SENSITIVITY)

    def signal_handler(self, signal, frame):
        self.INTERRUPTED = True

    def interrupt_callback(self):
        return self.INTERRUPTED or self.FINISHED_PROCESSING_JOB

    def main(self):
        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        while not self.INTERRUPTED:
            self.FINISHED_PROCESSING_JOB = False
            logging.info("Listening for hotword...")
            self.detector.start(detected_callback=self.listen_for_job, interrupt_check=self.interrupt_callback, sleep_time=0.03)
        self.detector.terminate()

    def listen_for_job(self):
        self.detector.terminate()
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            logging.info("Listening for main question...")
            self.response_library.ding()
            audio = r.listen(source)
            self.response_library.ding(True)
        try:
            logging.info("Sending voice to Google")
            question = r.recognize_google(audio).lower()
            logging.info("Google thinks you said: " + question)
            print("Q: " + question)
            self.process_job(question)
        except sr.UnknownValueError:
            logging.error("There was a problem whilst processing your question")
        self.create_detector()
        self.FINISHED_PROCESSING_JOB = True


    def process_job(self, question):
        has_response = False
        for module in self.modules:
            if module.should_action(None, question):
                self.response_library.ding(True)
                module.action(None, question)
                # Potentially don't break here, depends if multiple modules should action something or not?
                has_response = True
                break

        if not has_response:
            for module in self.modules:
                if module.is_catchall:
                    module.action(None, question)




if __name__ == "__main__":
    import setup_logging
    vc = VoiceController()
    vc.main()
    #vc.process_job("play me some music")
