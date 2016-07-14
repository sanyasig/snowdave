import snowboydecoder
import sys
import signal
import pyaudio
from voiceProcessor import VoiceProcessor

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

model = "resources/Alexa.pmdl"
vr = VoiceProcessor()
vr.getQuestion()
#vr.askQuestion("turn on tv")

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.40)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=vr.getQuestion,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
