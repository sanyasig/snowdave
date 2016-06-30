import sys
from wit import Wit


class ProcesQuestion:

    def __init__(self):
        self.analiser = Wit(access_token="AWA3HYBQZ7YMCAZD7WRMHISDQAZWVXTN", actions=self.actions)

    def send(self, request, response):
        print('Sending to user...', response['text'])

    def setTimer(self,request, response):
        print(' mmy action Received from user...', request['text'])

    def getWeather(self):
        print ("this gets weather")

    actions = {
        'send': send,
        'my_action': setTimer,
        "getWeather": setTimer,
        "setTimer": setTimer,
        "test": setTimer,
    }

    def analiseQuestion(self, question):
        response = self.analiser.message(question);
        print ("wit.ai responded" + response);




