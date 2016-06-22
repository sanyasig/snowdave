import pyttsx
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from Google_TTS import GoogleTTS

class Speech:

    engine = None
    googleEngine= None

    def __init__(self, engine=None):
        self.engine = engine
        self.googleEngine = GoogleTTS()


    def init_pyttsx(self):
        engine = pyttsx.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 50)


    def google_say(self, text):
        audio_file = "output.mp3"
        self.googleEngine.audio_extract(text)
        self.play_mp3(audio_file)


    def pyttsx_say(self, say):
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id)
        self.engine.say('Did you want something?')
        # engine.runAndWait()
        self.engine.startLoop(True)
        self.engine.iterate()

    def play_mp3(self, audio_file):
        audioStream = AudioSegment.from_mp3(audio_file)
        play(audioStream)


