from BaseVoiceControllerModule import BaseVoiceControllerModule
from xbmcjson import XBMC, PLAYER_VIDEO
import subprocess

class KodiController(BaseVoiceControllerModule):
    KODI_SERVER = "http://localhost:8080"

    def __init__(self):
        self.xbmc = XBMC(self.KODI_SERVER + "/jsonrpc")

    def should_action(self, keyword, question):
        return "kodi" in question or "xbmc" in question

    def action(self, keyword, question):
        print "Doing some stuff with mopidy"

        if self.contains_start_word(question):
            self.response.say("Starting up kodi")
            self.start_kodi()
        elif self.contains_stop_word(question):
            self.response.say("Exiting kodi")
            self.stop_kodi()
        elif "find album" in question:
            self.find_album(question)
        else:
            self.response.say("Sorry I didn't understand that")

    def start_kodi(self):
        CREATE_NEW_CONSOLE = 0x00000010
        pid = subprocess.Popen(["kodi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).pid #, creationflags=CREATE_NEW_CONSOLE (windows)

    def stop_kodi(self):
        self.xbmc.Application.Quit()

    def find_album(self, query):
        albums = self.xbmc.AudioLibrary.GetAlbums({"filter": { "artist": question[question.index(" by ") + 4:]}})
        if len(albums["result"]) > 0 and len(albums["result"]["albums"]) > 0:
            answer = "Playing the first album found, but I found the following albums: "
            count = 0
            for album in albums["result"]["albums"]:
                if count > 0:
                    answer += " and "
                else:
                    self.xbmc.Player.Open({"item": {"albumid": album["albumid"] }})
                answer += "Album %s: %s. " % ((count + 1), album["label"])
                count += 1

        else:
            answer = "Couldn't find any albums by that artist"
