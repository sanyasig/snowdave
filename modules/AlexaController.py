from BaseVoiceControllerModule import BaseVoiceControllerModule
import requests
import logging
import json
import time
import re
import os

from tempfile import NamedTemporaryFile
from io import BytesIO
import stat

class AlexaController(BaseVoiceControllerModule):
    is_catchall = True

    def should_action(self, keyword, question):
        return self.get_witai_item(witai, "intent") in ["time", "joke", "weather"]
        return False

    def action(self, keyword, question, audioData):
        audioBytes = audioData.get_wav_data()
        fObj = BytesIO(audioBytes)

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
        
        files = [
                ('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
                ('file', ('audio', fObj, 'audio/L16; rate=16000; channels=1'))
                ]
        r = requests.post(url, headers=headers, files=files)
        fObj.close()
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

            self.response.play_mp3_data(audio)

        else:
            logging.error("Alexa Miserable Failure")
            logging.error(r.status_code)
            return False

    def gettoken(self):
        token_cache_fname = "token_cache.txt"
        token = None
        #Time difference is in seconds
        if os.path.exists(token_cache_fname) and time.time() - os.stat(token_cache_fname)[stat.ST_MTIME] < 300:
            fObj = open(token_cache_fname, "r")
            token = fObj.read()
            fObj.close()
        refresh = self.config["refresh_token"]
        if token:
            logging.debug("I have a cached token: %s" % token)
            return token
        elif refresh:
            payload = {"client_id" : self.config["Client_ID"], "client_secret" : self.config["Client_Secret"], "refresh_token" : refresh, "grant_type" : "refresh_token", }
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
