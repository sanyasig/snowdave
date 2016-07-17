import paho.mqtt.client as paho
from enum import Enum

class MqttTopics(Enum):
    tv_on = "turn-on"
    tv_off = "turn-off"
    tv_volume_up = "Volume-up"
    tv_volume_down = "Volume-down"


class MqttManager:

    def on_publish(client, userdata, mid):
        print("mid: " + str(mid))
    #
    # client = paho.Client()
    # client.on_publish = on_publish
    # client.connect('192.168.0.3', 1883)

    def __init__(self):
        print "init of mqttMessanger"
        # self.mqtt_server_url = "192.168.0.3"
        #
        # self.client.loop_start()

    def controlTV(self, message):
        print "stuff i get " + message
       # (rc, mid) = self.client.publish('esp_ir', message, qos=1)




