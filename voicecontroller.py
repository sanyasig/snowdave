import pyttsx
import signal
#from pydub import AudioSegment
import speech_recognition as sr
import logging
import os
import sys
import traceback

import modules
from modules import *
from wit import Wit
import requests
import audioop

from gtts import gTTS
from tempfile import NamedTemporaryFile
from io import BytesIO
import subprocess

from config import *

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
        #Force using pulse audio
        subprocess.Popen(['mpg123', '-o', 'pulse', '-q', fname]).wait()


class VoiceController:
    MODEL = "lib/resources/Alexa.pmdl"
    SENSITIVITY = 0.5
    INTERRUPTED = False
    FINISHED_PROCESSING_JOB = True
    
    def __init__(self):
        self.create_detector()
        self.response_library = ResponseLibrary()
        self.witClient = Wit(access_token=WIT_API_KEY)

        self.recignisor = sr.Recognizer()
        #Tweak everything to make it fast :D
        self.recignisor.non_speaking_duration = 0.4
        self.recignisor.pause_threshold = 0.5
        self.recignisor.energy_threshold = 2500
        self.recignisor.dynamic_energy_threshold = True

        self.adjust_for_ambient(2)

        self.modules = []
        for module in modules.__all__:
            logging.info("Loading module: " + module)
            moduleInstance = eval(module + "." + module + "()")
            moduleInstance.set_response_library(self.response_library)
            self.modules.append(moduleInstance)

    def adjust_for_ambient(self, time=0.5):
        #return #Temp disabled
        with self.get_microphone() as source:
            self.recignisor.adjust_for_ambient_noise(source, time)

    def get_microphone(self):
        #Force using PS3 Eye camera mic
        m = sr.Microphone() #Have to make an object before u can then inspect others, coz, no reason . . .
        mics = m.list_microphone_names()
        index = 0
        for i in range(0, len(mics)):
            logging.debug("Available mic: %s" % mics[i])
            if mics[i].startswith("pulse"): #USB Camera-B4.09.24.1: Audio
                logging.debug("Using mic: %s" % mics[i])
                index = i
                break
        return sr.Microphone(i, sample_rate = 16000, chunk_size = 1024)

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
                self.process_job(raw_input("Question: "))
            return

        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        if not "noready" in sys.argv:
            self.response_library.say("Ready")
        while not self.INTERRUPTED:
            self.FINISHED_PROCESSING_JOB = False
            logging.info("Listening for hotword...")
            self.detector.start(detected_callback=self.listen_for_job, interrupt_check=self.interrupt_callback, sleep_time=0.03)
        self.detector.terminate()


    def listen_for_job(self):
        self.detector.terminate()
        audio = None

        with self.get_microphone() as source:
            logging.info("Listening for main question...")
            self.response_library.ding()
            try:
                audio = self.recignisor.listen(source, timeout=5)
                self.response_library.ding(True)
            except sr.WaitTimeoutError: self.response_library.say("Sorry I didn't hear anything")

        if audio:
            try:
                logging.info("Sending voice to Google")

                question = self.recignisor.recognize_google(audio).lower()
                witResponse = self.witClient.message(question) #run_actions(session_id, question)

                #This was much slower
                #witResponse = r.recognize_wit(audio, WIT_API_KEY, show_all=True)
                #question = witResponse["_text"].lower()
                #witResponse = witResponse["outcomes"][0]

                logging.info("Google thinks you said: " + question)
                print("Q: " + question)
                self.process_job(question, witResponse, audio)
            except sr.UnknownValueError, e:
                logging.error("There was a problem whilst processing your question")
                logging.error(traceback.print_stack())
                self.response_library.say("There was a problem whilst processing your question")
        self.create_detector()
        self.FINISHED_PROCESSING_JOB = True


    def process_job(self, question, witResponse=None, audio=None):
        has_response = False
        for module in self.modules:
            if module.should_action(witResponse, question):
                self.response_library.ding(True)
                try: module.action(witResponse, question)
                except Exception, e:
                    logging.error(traceback.print_stack())
                    self.response_library.say("Something went wrong! %s" % str(e).split("\n")[0])
                # Potentially don't break here, depends if multiple modules should action something or not?
                has_response = True
                break

        if not has_response:
            for module in self.modules:
                if module.is_catchall:
                    self.response_library.ding(True)
                    try: module.action(witResponse, question, audio)
                    except Exception, e:
                        logging.error(traceback.print_stack())
                        self.response_library.say("Something went wrong! %s" % str(e).split("\n")[0])

        self.adjust_for_ambient()
        self.response_library.ding(True)




if __name__ == "__main__":
    import setup_logging
    vc = VoiceController()
    vc.main()
    #vc.process_job("play me some music")
