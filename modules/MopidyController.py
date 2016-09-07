from BaseVoiceControllerModule import BaseVoiceControllerModule

import requests
import random

# See http://mopidy.readthedocs.io/en/latest/api/core/#core-api
# Also checkout https://bitbucket.org/pyglet/pyglet/wiki/Home
# See - https://github.com/hey-athena/hey-athena-client/blob/demo-branch/athena/tts.py for an example of pyglet

class MopidyController(BaseVoiceControllerModule):
    SERVER = "http://localhost:6680/mopidy/rpc"

    def should_action(self, witai, question):
        return self.get_witai_item(witai, "intent") in ["music", "tune", "play me", "mopidy"]

    def action(self, witai, question, audio):
        print "Doing some stuff with mopidy"
        action = self.get_witai_item(witai, "action")
        search_query = self.get_witai_item(witai, "search_query")

        if "ash" in question:
            self.response.say("Playing Ash's Playlist")
            self.play_playlist(name="Ash")
        elif "playlist" in action:
            self.response.say("Playing Playlist")
            #Should handle: 'play me the ashley playlist' and 'music playlist bob'
            self.play_playlist(name=search_query)
        elif "some" in question and not "some music" in question:
            self.response.say("Playing Genre")
            searchFor = filter(None, question.replace(" music", "").split("play me some"))[0].strip()
            self.search_by_genre(searchFor)
        elif "artist" in action:
            self.response.say("Searching for artist")
            self.search_by_artist(search_query)
        elif "search" in action:
            self.response.say("Searching")
            self.search(search_query)
        elif "pause" in action:
            self.pause_music()
        elif "resume" in action:
            self.resume_music()
        elif "next" in action:
            self.next_track()
        elif "previous" in action:
            self.previous_track()
        elif "volume" in action:
            if "down" in question:
                self.response.say("Turning it down")
                self.turn_down()
            elif "up" in question:
                self.response.say("Turning it up")
                self.turn_up()
        elif "play" in action:
            self.response.say("Loading some music")
            self.play_random_playlist()
        elif "stop" in action:
            self.stop_music()
        else:
            self.response.say("Sorry I didn't understand that")

    def search(self, query):
        #albums artists tracks any
        return self.search_with_keyword("any", query)

    def search_by_genre(self, query):
        return self.search_with_keyword("genre", query)

    def search_by_artist(self, query):
        return self.search_with_keyword("artist", query)

    def search_with_keyword(self, keyword, query):
        #Note currently limiting to spotify, due to the HUGE potential music possibility due to podcasts
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.library.search", "params": { keyword: [query], "uris": ['spotify:']}})
        urisToAdd = self.get_items_from_results(r)
        if len(urisToAdd) == 0:
            self.response.say("Nothing found")
            return
        self.stop_music()
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.add", "params": {"uris": urisToAdd }})
        self.turn_on_shuffle_and_play()


    def get_items_from_results(self, r):
        result = r.json()["result"]
        if len(result) == 0:
            print "Nothing found matching query!"
            return

        urisToAdd = []
        for searchResultType in result:
            for resultKey in searchResultType:
                if resultKey.startswith("_") or resultKey == "uri":
                    continue
                for item in searchResultType[resultKey]:
                    try: urisToAdd.append(item["uri"])
                    except Exception, e: pass
        return urisToAdd


    def getPlaybackState(self):
        #curl -d '{"jsonrpc": "2.0", "id": 1, "method": "core.playback.get_state"}' http://dave/mopidy/rpc
        pass

    def play_random_playlist(self):
        self.play_playlist(name=None)

    def play_playlist(self, name=None, count=0):
        if (count > 2):
            print "Tried 3 playlist, all were too short, giving up"
            return
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.clear", "params": {}})
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.playlists.get_playlists", "params": {"include_tracks": "false"}})
        result = r.json()["result"]
        if len(result) == 0:
            print "No playlists found!"
            return

        playlist = random.choice(result)
        if name:
            for item in result:
                if name.lower() in item["name"].lower():
                    playlist = item
                    break

        print "Playing: " + playlist["name"]
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.add", "params": {"uri": playlist["uri"] }})
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.get_length", "params": {}})
        result = r.json()["result"]
        if not name and result <= 3:
            print "Chosen playlist too short, changing"
            count += 1
            return self.play_playlist(count=count)

        self.turn_on_shuffle_and_play()


    def turn_on_shuffle_and_play(self):
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.shuffle", "params": {}})
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.play", "params": {}})

    def pause_music(self):
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.pause", "params": {}})

    def resume_music(self):
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.resume", "params": {}})

    def stop_music(self):
        #May or may not want to clear the playlist, but might as well save some memory :)
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.clear", "params": {}})
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.playback.stop", "params": {}})

    def next_track(self):
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.next_track", "params": {}})

    def previous_track(self):
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.tracklist.previous_track", "params": {}})

    def turn_down(self):
        self.adjust_volume(-10)

    def turn_up(self):
        self.adjust_volume(10)

    def adjust_volume(self, change):
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.mixer.get_volume", "params": {}})
        currentVolume = r.json()["result"]

        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.mixer.set_volume", "params": {"volume": currentVolume+change}})
