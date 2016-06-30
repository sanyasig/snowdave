import wolframalpha
import speech_recognition as sr
import time


from speech import Speech
from wit import Wit
from processQuestion import ProcesQuestion
class VoiceProcessor:

    def __init__(self):
        self.recigniser = sr.Recognizer()
        self.mic = sr.Microphone()
        self.say = Speech()
        self.analizeQuestion = ProcesQuestion()
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
        response = self.analizeQuestion.analiseQuestion(question)

        # if len(res.pods) > 0:
        #     pod = res.pods[1]
        #     if pod.text:
        #         answer = pod.text.encode("ascii", "ignore")
        #         print ("answer to the question is " + answer)
        #         self.say.google_say(answer);

