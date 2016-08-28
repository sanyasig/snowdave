import speech_recognition as sr
import logging

from wit import Wit
import pyaudio
import math
import requests
import audioop
import json

import os
from io import BytesIO

WIT_API_HOST = os.getenv('WIT_URL', 'https://api.wit.ai')
WIT_API_VERSION = os.getenv('WIT_API_VERSION', '20160516')

class WitError(Exception):
    pass

def voiceReq(logger, access_token, meth, path, params, **kwargs):
    full_url = WIT_API_HOST + path
    logger.debug('%s %s %s', meth, full_url, params)
    rsp = requests.request(
        meth,
        full_url,
        headers={
            'authorization': 'Bearer ' + access_token,
            'accept': 'application/vnd.wit.' + WIT_API_VERSION + '+json',
            #'Content-type': 'audio/wav',
            'Content-type': 'audio/raw; encoding=signed-integer; bits=16; rate=8000; endian=little',
            'Transfer-Encoding': 'chunked',
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
    completeRecording = b""

    def get_most_recent_recording(self):
        SAMPLE_WIDTH = pyaudio.get_sample_size(pyaudio.paInt16)
        SAMPLE_RATE = 16000
        return sr.AudioData(self.completeRecording, SAMPLE_RATE, SAMPLE_WIDTH)

    def voiceMessage(self, audio, verbose=None):
        audioBytes = audio.get_wav_data()
        fObj = BytesIO(audioBytes)
        params = {}
        if verbose:
            params['verbose'] = True
        resp = voiceReq(self.logger, self.access_token, 'POST', '/speech', params, data=fObj)
        fObj.close()
        return resp

    def readFromStream(self, source):
        assert source.stream is not None, "Audio source must be entered before listening, see documentation for `AudioSource`; are you using `source` outside of a `with` statement?"
        self.completeRecording = b""

        #source.SAMPLE_RATE, source.SAMPLE_WIDTH
        pause_threshold = 0.6
        energy_threshold = 400
        seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        pause_buffer_count = int(math.ceil(pause_threshold / seconds_per_buffer))
        buffer = b""

        foundAnyAudioYet = False
        elapsed_time = 0
        pause_count = 0
        print "Reading from stream"
        while True:
            elapsed_time += seconds_per_buffer
            if elapsed_time > 5: # handle timeout if specified
                raise Exception("Nothing was said")
            buffer = source.stream.read(source.CHUNK)
            self.completeRecording += buffer
            if len(buffer) == 0: break # reached end of the stream

            # check if speaking has stopped for longer than the pause threshold on the audio input
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH) # energy of the audio signal
            if energy > energy_threshold:
                pause_count = 0
                foundAnyAudioYet = True
            else:
                pause_count += 1
            if foundAnyAudioYet and pause_count > pause_buffer_count: # end of the phrase
                break
            yield buffer

        #yield from stream.read()
        print "Finished recording"

    def voiceMessageStream(self, source, verbose=None):
        params = {}
        if verbose:
            params['verbose'] = True
        resp = voiceReq(self.logger, self.access_token, 'POST', '/speech', params, data=self.readFromStream(source), stream=True)
        return resp

class QuestionInterpreter:
    def __init__(self, wit_api_key):
        self.witClient = WitWithVoice(access_token=wit_api_key)
        self.recignisor = sr.Recognizer()
        #Tweak everything to make it fast :D
        self.recignisor.non_speaking_duration = 0.5
        self.recignisor.pause_threshold = 0.6
        self.recignisor.dynamic_energy_threshold = True
        self.recignisor.energy_threshold = 400

    def get_question_from_mic(self): #throws sr.UnknownValueError
        r = self.recignisor

        audio = None
        with sr.Microphone(sample_rate = 8000, chunk_size = 4096) as source:
            logging.info("Listening for main question...")
            witResponse = self.witClient.voiceMessageStream(source)
            print "Got response from WIT"
            audio = self.witClient.get_most_recent_recording()
            print witResponse

            #See https://github.com/ilar/Wit.Ai-Chunked/blob/master/uploadPyAudio.py for working library
            #audio = r.listen(source, timeout=5)

        #question = r.recognize_google(audio).lower()
        #witResponse = r.recognize_wit(audio, WIT_API_KEY, show_all=True)
        question = witResponse["_text"].lower()
        logging.info("Interpreter thinks you said: " + question)
        print("Q: " + question)
        return (question, witResponse, audio)


if __name__ == "__main__":
    import setup_logging
    with open('config.json') as data_file:    
        data = json.load(data_file)
    qi = QuestionInterpreter(data["main"]["WIT_API_KEY"])
    (question, witResponse, audio) = qi.get_question_from_mic()
