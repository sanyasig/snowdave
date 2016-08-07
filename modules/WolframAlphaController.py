from BaseVoiceControllerModule import BaseVoiceControllerModule
import wolframalpha

class WolframAlphaController(BaseVoiceControllerModule):
    WOLFRAM_ALPHA_KEY = "QQG9XK-5HQA4Q3257"
    is_catchall = True

    def __init__(self):
        self.wolfram_client = wolframalpha.Client(self.WOLFRAM_ALPHA_KEY)

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        res = self.wolfram_client.query(question)
        if len(res.pods) > 0:
            pod = res.pods[1]
            if pod.text:
                answer = pod.text.encode("ascii", "ignore")
                self.response.say(answer)

