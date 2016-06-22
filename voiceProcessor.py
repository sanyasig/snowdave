import wolframalpha
import speech_recognition as sr
import time
from speech import Speech


class VoiceProcessor:
    WOLFRAM_ALPHA_KEY = "QQG9XK-5HQA4Q3257"

    def __init__(self):
        self.recigniser = sr.Recognizer()
        self.mic = sr.Microphone()
        self.say = Speech()
        self.wolfram_client = wolframalpha.Client(self.WOLFRAM_ALPHA_KEY)
        with self.mic as source:
            self.recigniser.adjust_for_ambient_noise(source)


    def getQuestion(self):
        # have to analize the question being asked
        self.process_command()


    def process_command(self):
        time.sleep(0.2)
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.recigniser.adjust_for_ambient_noise(source)
            print("Listening!")
            audio = r.listen(source)
        try:
            question = r.recognize_google(audio).lower()
            print("Google Thinks you said : " + question)
            self.askQuestion(question)
        except sr.UnknownValueError:
            print("google could not Recognise what you said")


    def askQuestion(self, question):
        print (question)
        res = self.wolfram_client.query(question)
        if len(res.pods) > 0:
            pod = res.pods[1]
            if pod.text:
                answer = pod.text.encode("ascii", "ignore")
                print ("answer to the question is " + answer)
                self.say.google_say(answer);



