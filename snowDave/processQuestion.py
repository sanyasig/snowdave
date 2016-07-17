import unicodedata

import wolframalpha
from wit import Wit

from actions import Actions


class ProcesQuestion:
    WOLFRAM_ALPHA_KEY = "QQG9XK-5HQA4Q3257"
    WIT_AI_KEY = "AWA3HYBQZ7YMCAZD7WRMHISDQAZWVXTN"
    OPEN_WEATHER_KEY = "3fb5245d6b9dcdd8d18d230bb12e4bff"


    def __init__(self):
        self.analiser = Wit(access_token=self.WIT_AI_KEY, actions=self.witActions)
        self.wolfram_client = wolframalpha.Client(self.WOLFRAM_ALPHA_KEY)
        self.action = Actions();


    def send(self, request, response):
        print('Sending to user...', response['text'])

    witActions = {
        'send': send,
    }

    def analiseQuestion(self, question):
        wit_response = self.analiser.message(question);
        response = "";
        print wit_response
        entities = wit_response['entities']

        if(self.action.isHandeledByDave(entities)):
             response = self.action.callAction(entities)

        else:
            res = self.wolfram_client.query(question)
            if len(res.pods) > 0:
                pod = res.pods[1]
                if pod.text:
                    response = pod.text.encode("ascii", "ignore")
            print response

        return response;

    def convertUnicode(self, value):
        return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')




