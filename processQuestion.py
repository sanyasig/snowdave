import sys

import wolframalpha
from wit import Wit
import unicodedata
import requests
import ast

class ProcesQuestion:
    WOLFRAM_ALPHA_KEY = "QQG9XK-5HQA4Q3257"
    WIT_AI_KEY = "AWA3HYBQZ7YMCAZD7WRMHISDQAZWVXTN"
    OPEN_WEATHER_KEY = "3fb5245d6b9dcdd8d18d230bb12e4bff"

    def __init__(self):
        self.analiser = Wit(access_token=self.WIT_AI_KEY, actions=self.actions)
        self.wolfram_client = wolframalpha.Client(self.WOLFRAM_ALPHA_KEY)


    def send(self, request, response):
        print('Sending to user...', response['text'])


    def setTimer(self,entities):
        print(' mmy action Received from user...text')


    def getWeather(self, entities):
        location = self.convertUnicode(entities['location'][0]['value'])
        weather_url = "http://api.openweathermap.org/data/2.5/weather?q=%s,uk&appid=%s&units=metric" %(location, self.OPEN_WEATHER_KEY)
        response = requests.get(weather_url)
        weather_report = 'its '
        if(response.status_code == 200):
            weather =  ast.literal_eval(response.content)
            weather_report += weather["weather"][0]['description'] + " , with a "
            weather_report += "maximum of " + str(weather['main']["temp_max"]) + " and a minimum of " + str(weather['main']["temp_min"])
        return weather_report


    actions = {
        'send': send,
        "weather": getWeather,
        "setTimer": setTimer,
    }


    def analiseQuestion(self, question):
        wit_response = self.analiser.message(question);
        response = "";
        entities = wit_response['entities']
        if("intent" in entities):
            intent = entities['intent'][0]
            intent_string  = self.convertUnicode(intent['value'])

            if intent_string in self.actions:
                response = self.actions[intent_string](self, entities)
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




