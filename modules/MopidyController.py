from BaseVoiceControllerModule import BaseVoiceControllerModule

import requests
import random

# See http://mopidy.readthedocs.io/en/latest/api/core/#core-api
# Also checkout https://bitbucket.org/pyglet/pyglet/wiki/Home
# See - https://github.com/hey-athena/hey-athena-client/blob/demo-branch/athena/tts.py for an example of pyglet

class MopidyController(BaseVoiceControllerModule):
    SERVER = "http://dave/mopidy/rpc"

    def should_action(self, keyword, question):
        return "music" in question or "tune" in question

    def action(self, keyword, question):
        print "Doing some stuff with mopidy"

        if "ash" in question:
            self.play_playlist(name="Ash")
        elif "play" in question:
            self.play_random_playlist()
        elif "stop" in question:
            self.stop_music()
        elif "pause" in question:
            self.pause_music()
        elif "resume" in question:
            self.resume_music()
        elif "next" in question:
            self.next_track()
        elif "previous" in question:
            self.previous_track()
        else:
            self.response.say("Sorry I didn't understand that")

    def search(self, query):
        #curl -d '{"jsonrpc": "2.0", "id": 1, "method": "core.library.search", "params": { "any": ["wilkinson"]}}' http://dave/mopidy/rpc
        #albums artists tracks any
        r = requests.post(self.SERVER, json={"jsonrpc": "2.0", "id": 1, "method": "core.library.search", "params": { "any": [query]}})
        print r.text
        print "-"*50
        print r.json()

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
