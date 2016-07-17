import requests
import ast

import unicodedata
from mqttManager import  MqttManager, MqttTopics

class Actions:

    def __init__(self):
        self.mqttManager = MqttManager()

    def setTimer(self, entities):
        print(' mmy action Received from user...text')


    def getWeather(self, entities):
        location = self.convertUnicode(entities['location'][0]['value'])
        weather_url = "http://api.openweathermap.org/data/2.5/weather?q=%s,uk&appid=%s&units=metric" % (
        location, self.OPEN_WEATHER_KEY)
        response = requests.get(weather_url)
        weather_report = 'its '

        if (response.status_code == 200):
            weather = ast.literal_eval(response.content)
            weather_report += weather["weather"][0]['description'] + " , with a "
            weather_report += "maximum of " + str(weather['main']["temp_max"]) + " and a minimum of " + str(
                weather['main']["temp_min"])

        return weather_report


    def toggleTv(self, entities):
        action = self.convertUnicode(entities['on_off'][0]['value'])

        if (action == "on"):
            self.mqttManager.controlTV(MqttTopics.tv_on)
        else:
            self.mqttManager.controlTV(MqttTopics.tv_off)

        return "done"

    actions = {
        "weather": getWeather,
        "setTimer": setTimer,
        "toggle_tv": toggleTv
    }


    def callAction (self, entities):
        intent = entities['intent'][0]
        intent_string = self.convertUnicode(intent['value'])
        return self.actions[intent_string](self, entities)


    def isHandeledByDave(self, entities):
        isValidAction = False

        if "intent" in entities:
            intent = entities['intent'][0]
            confidence = intent['confidence']
            intent_string = self.convertUnicode(intent['value'])
            isValidAction = intent_string in self.actions

        if isValidAction and  (confidence > 0.8):
            return True
        return False


    def convertUnicode(self, value):
        return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')




