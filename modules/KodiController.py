from BaseVoiceControllerModule import BaseVoiceControllerModule
from xbmcjson import XBMC, PLAYER_VIDEO
import subprocess

class KodiController(BaseVoiceControllerModule):
    KODI_SERVER = "http://localhost:8080"
    STANDARD_SORT = {"order": "ascending", "method": "title", "ignorearticle": True}

    def __init__(self):
        self.xbmc = XBMC(self.KODI_SERVER + "/jsonrpc")

    def should_action(self, witai, question):
        return self.is_my_intent(witai, "kodi")
        #return "kodi" in question or "xbmc" in question

    def action(self, intent, question):
        print "Doing some stuff with kodi"
        action = self.get_witai_item(witai, "action")
        search_query = self.get_witai_item(witai, "search_query")

        if self.contains_start_word(action):
            self.response.say("Starting up kodi")
            self.start_kodi()
        elif self.contains_stop_word(action):
            self.response.say("Exiting kodi")
            self.stop_kodi()
        elif search_query:
            episode = None
            season = None
            if "number" in intent["entities"]:
                episode = intent["entities"]["number"][0]["value"]
                if len(intent["entities"]["number"]) > 1:
                    season = intent["entities"]["number"][1]["value"]
            self.play_video(search_query, season, episode)

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

    def stop_playback(self):
        playerid = self.xbmc.Player.GetActivePlayers()["result"]
        if len(playerid) > 0:
            playerid = playerid[0]["playerid"]
            self.xbmc.Player.Stop({"playerid": playerid })

    def play_video(self, name, season=None, episode=None):
        videos = []
        if not season and not episode:
            videos = self.xbmc.VideoLibrary.GetMovies({"sort": self.STANDARD_SORT, "filter": {"operator": "contains", "field": "title", "value": name}})["result"]

        if len(videos) > 0 and "movies" in videos and len(videos["movies"]) > 0:
            item = videos["movies"][0]
            self.xbmc.Player.Open({"item": {"movieid": item["movieid"] }})
            self.response.say("Playing " + item["label"])

        else:
            videos = self.xbmc.VideoLibrary.GetTVShows({"sort": self.STANDARD_SORT, "filter": {"operator": "contains", "field": "title", "value": name}})["result"]
            if len(videos) > 0 and "tvshows" in videos and len(videos["tvshows"]) > 0:
                tvshowid = videos["tvshows"][0]["tvshowid"]
                args = {"sort": self.STANDARD_SORT, "tvshowid": tvshowid}
                if season:
                    args["season"] = season
                if episode:
                    args["filter"] = {"operator": "contains", "field": "episode", "value": str(episode)}
                videos = self.xbmc.VideoLibrary.GetEpisodes(args)["result"]
                if len(videos) > 0:
                    item = videos["episodes"][0]
                    self.xbmc.Player.Open({"item": {"episodeid": item["episodeid"] }})
                    self.response.say("Playing " + item["label"])
            else:
                self.response.say("Sorry I could not find what you are looking for")
