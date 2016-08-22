import pyttsx
import signal
#from pydub import AudioSegment
import speech_recognition as sr
import logging
import os
import traceback

import modules
from modules import *
from wit import Wit
import requests

from gtts import gTTS
from tempfile import NamedTemporaryFile
from io import BytesIO
import subprocess

if os.name != "nt":
    from lib import snowboydecoder

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
        #if self.ENGINE == "google":
        try:
            tts = gTTS(text=message, lang='en')
            f = NamedTemporaryFile(suffix=".mp3")
            tts.write_to_fp(f)
            f.flush()
            self.play_mp3(f.name)
            f.close()
        #else:
        except requests.exceptions.HTTPError:
            self.pyttsx_engine.say(message)
            self.pyttsx_engine.runAndWait()

    def ding(self, dong=False):
        if os.name != "nt":
            sound = snowboydecoder.DETECT_DONG if dong else snowboydecoder.DETECT_DING
            self.play_wav(sound)

    def play_wav(self, sound):
        snowboydecoder.play_audio_file(sound)

    def play_mp3_data(self, audioData):
        f = NamedTemporaryFile(suffix=".mp3")
        f.write(audioData)
        f.flush()
        self.play_mp3(f.name)
        f.close()

    def play_mp3(self, fname):
        subprocess.Popen(['mpg123', '-q', fname]).wait()

class VoiceController:
    MODEL = "lib/resources/Alexa.pmdl"
    SENSITIVITY = 0.5
    INTERRUPTED = False
    FINISHED_PROCESSING_JOB = True
    
    def __init__(self):
        self.create_detector()
        self.response_library = ResponseLibrary()
        self.witClient = Wit(access_token="2GZ3OP3K2CIWQNH3W6GJDAEXET63AXUA")

        self.modules = []
        for module in modules.__all__:
            logging.info("Loading module: " + module)
            moduleInstance = eval(module + "." + module + "()")
            moduleInstance.set_response_library(self.response_library)
            self.modules.append(moduleInstance)

    def create_detector(self):
        if os.name != "nt":
            self.detector = snowboydecoder.HotwordDetector(self.MODEL, resource="lib/resources/common.res", sensitivity=self.SENSITIVITY)

    def signal_handler(self, signal, frame):
        self.INTERRUPTED = True

    def interrupt_callback(self):
        return self.INTERRUPTED or self.FINISHED_PROCESSING_JOB

    def main(self):
        if os.name == "nt":
            while not self.INTERRUPTED:
                self.process_job(raw_input("Question: "), None)
            return

        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        self.response_library.say("Ready")
        while not self.INTERRUPTED:
            self.FINISHED_PROCESSING_JOB = False
            logging.info("Listening for hotword...")
            self.detector.start(detected_callback=self.listen_for_job, interrupt_check=self.interrupt_callback, sleep_time=0.03)
        self.detector.terminate()

    def listen_for_job(self):
        self.detector.terminate()
        r = sr.Recognizer()
        audio = None
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
            self.process_job(question, audio)
        except sr.UnknownValueError:
            logging.error("There was a problem whilst processing your question")
        self.create_detector()
        self.FINISHED_PROCESSING_JOB = True


    def process_job(self, question, audio):
        #session_id = uuid.uuid1()

        witResponse = self.witClient.message(question) #run_actions(session_id, question)
        print witResponse
        has_response = False
        for module in self.modules:
            if module.should_action(witResponse, question):
                self.response_library.ding(True)
                try: module.action(witResponse, question)
                except Exception, e:
                    logging.error(traceback.print_stack())
                    self.response_library.say("Something went wrong! %s" % e)
                # Potentially don't break here, depends if multiple modules should action something or not?
                has_response = True
                break

        if not has_response:
            for module in self.modules:
                if module.is_catchall:
                    module.action(witResponse, question, audio)




if __name__ == "__main__":
    import setup_logging
    vc = VoiceController()
    vc.main()
    #vc.process_job("play me some music")
