import paho.mqtt.client as mqtt
from enum import Enum

class MqttTopics(Enum):
    tv_on = "turn-on"
    tv_off = "turn-off"
    tv_volume_up = "Volume-up"
    tv_volume_down = "Volume-down"


class MqttManager:

    def __init__(self):
        self.mqtt_server_url = "192.168.0.3"

    def controlTV(self, message):
        print "stuff i get " + message

