import time

import speech_recognition as sr

import processQuestion as processQuestion
from speech import Speech


class VoiceProcessor:


    def __init__(self):
        self.recigniser = sr.Recognizer()
        self.mic = sr.Microphone()
        self.say = Speech()
        self.analizeQuestion = processQuestion.ProcesQuestion()
        with self.mic as source:
            self.recigniser.adjust_for_ambient_noise(source)


    def getQuestion(self):
        # have to analize the question being asked
        self.say.play_ding()
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
        if question != "":
            response = self.analizeQuestion.analiseQuestion(question)
        if(len(response) > 100):
            response = response[:99]

        if response != "":
            self.say.google_say(response)