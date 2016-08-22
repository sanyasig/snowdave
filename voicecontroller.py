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
        subprocess.Popen(['mpg123', '-q', fname]).wait()

def voiceReq(logger, access_token, meth, path, params, **kwargs):
    full_url = WIT_API_HOST + path
    logger.debug('%s %s %s', meth, full_url, params)
    rsp = requests.request(
        meth,
        full_url,
        headers={
            'authorization': 'Bearer ' + access_token,
            'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
            'Content-type': 'audio/wav'
        },
        params=params,
        **kwargs
    )
    if rsp.status_code > 200:
        raise WitError('Wit responded with status: ' + str(rsp.status_code) +
                       ' (' + rsp.reason + ')')
    json = rsp.json()
    if 'error' in json:
        raise WitError('Wit responded with an error: ' + json['error'])

    logger.debug('%s %s %s', meth, full_url, json)
    return json

class WitWithVoice(Wit):
    def voiceMessage(self, audio, verbose=None):
        audioBytes = audio.get_wav_data()
        fObj = BytesIO(audioBytes)
        params = {}
        if verbose:
            params['verbose'] = True
        resp = voiceReq(self.logger, self.access_token, 'POST', '/speech', params, data=fObj)
        fObj.close()
        return resp

class VoiceController:
    MODEL = "lib/resources/Alexa.pmdl"
    SENSITIVITY = 0.5
    INTERRUPTED = False
    FINISHED_PROCESSING_JOB = True
    
    def __init__(self):
        self.create_detector()
        self.response_library = ResponseLibrary()
        #self.witClient = WitWithVoice(access_token=WIT_API_KEY)

        self.recignisor = sr.Recognizer()
        #Tweak everything to make it fast :D
        self.recignisor.non_speaking_duration = 0.5
        self.recignisor.pause_threshold = 0.6
        self.recignisor.dynamic_energy_threshold = True
        self.recignisor.energy_threshold = 400

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
                self.process_job(raw_input("Question: "))
            return

        # capture SIGINT signal, e.g., Ctrl+C
        signal.signal(signal.SIGINT, self.signal_handler)
        self.response_library.say("Ready")
        while not self.INTERRUPTED:
            with sr.Microphone() as source:
                self.recignisor.adjust_for_ambient_noise(source)
            self.FINISHED_PROCESSING_JOB = False
            logging.info("Listening for hotword...")
            self.detector.start(detected_callback=self.listen_for_job, interrupt_check=self.interrupt_callback, sleep_time=0.03)
        self.detector.terminate()

    def listen_for_job(self):
        r = self.recignisor
        #self.detector.terminate()
        #r = sr.Recognizer()

        audio = None
        with sr.Microphone() as source:
            #r.adjust_for_ambient_noise(source)
            logging.info("Listening for main question...")
            self.response_library.ding()
            audio = r.listen(source, timeout=5)
            self.response_library.ding(True)
        try:
            logging.info("Sending voice to Google")
            #question = r.recognize_google(audio).lower()
            witResponse = r.recognize_wit(audio, WIT_API_KEY, show_all=True)
            question = witResponse["_text"].lower()
            witResponse = witResponse["outcomes"][0]
            logging.info("Google thinks you said: " + question)
            print("Q: " + question)
            self.process_job(question, witResponse, audio)
        except sr.UnknownValueError:
            logging.error("There was a problem whilst processing your question")
        #self.create_detector()
        self.FINISHED_PROCESSING_JOB = True


    def process_job(self, question, witResponse=None, audio=None):
        #witResponse = self.witClient.message(question) #run_actions(session_id, question)
        #witResponse = self.witClient.voiceMessage(audio)
        #print witResponse

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
                    try: module.action(witResponse, question, audio)
                    except Exception, e:
                        logging.error(traceback.print_stack())
                        self.response_library.say("Something went wrong! %s" % str(e).split("\n")[0])




if __name__ == "__main__":
    import setup_logging
    vc = VoiceController()
    vc.main()
    #vc.process_job("play me some music")
