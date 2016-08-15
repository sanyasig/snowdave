from BaseVoiceControllerModule import BaseVoiceControllerModule
import requests
import logging
import json
import re
import os

from config import *

class AlexaController(BaseVoiceControllerModule):
    is_catchall = True

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question, audioData):
        audioBytes = audioData.get_wav_data()
        fObj = open('recording.wav', "wb")
        fObj.write(audioBytes)
        fObj.close()

        url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
        headers = {'Authorization' : 'Bearer %s' % self.gettoken()}
        d = {
            "messageHeader": {
                "deviceContext": [
                    {
                        "name": "playbackState",
                        "namespace": "AudioPlayer",
                        "payload": {
                            "streamId": "",
                            "offsetInMilliseconds": "0",
                            "playerActivity": "IDLE"
                        }
                    }
                ]
            },
            "messageBody": {
                "profile": "alexa-close-talk",
                "locale": "en-us",
                "format": "audio/L16; rate=16000; channels=1"
            }
        }
        with open('recording.wav', "rb") as inf:
            files = [
                    ('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
                    ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
                    ]
            r = requests.post(url, headers=headers, files=files)
            print r
        if r.status_code == 200:
            logging.debug("Alexa: Victory is mine!")
            for v in r.headers['content-type'].split(";"):
                if re.match('.*boundary.*', v):
                    boundary =  v.split("=")[1]
            data = r.content.split(boundary)
            audio = data
            for d in data:
                if (len(d) >= 1024):
                    audio = d.split('\r\n\r\n')[1].rstrip('--')
            with open("response.mp3", 'wb') as f:
                f.write(audio)

            self.response.play_mp3("response.mp3")

        else:
            logging.error("Alexa Miserable Failure")
            logging.error(r.status_code)
            return False

    def gettoken(self):
        token_cache_fname = "token_cache.txt"
        token = None
        if os.path.exists(token_cache_fname):
            fObj = open(token_cache_fname, "r")
            token = fObj.read()
            fObj.close()
        refresh = refresh_token
        if token:
            logging.debug("I have a cached token: %s" % token)
            return token
        elif refresh:
            payload = {"client_id" : Client_ID, "client_secret" : Client_Secret, "refresh_token" : refresh, "grant_type" : "refresh_token", }
            url = "https://api.amazon.com/auth/o2/token"
            r = requests.post(url, data = payload)
            print "GOT A NEW TOKEN"
            print r.text
            resp = json.loads(r.text)
            fObj = open(token_cache_fname, "w")
            token = fObj.write(resp['access_token'])
            fObj.close()
            return resp['access_token']
        else:
            return False

