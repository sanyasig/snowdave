from BaseVoiceControllerModule import BaseVoiceControllerModule

class MorningController(BaseVoiceControllerModule):

    def should_action(self, entities, question):
        return ("good morning" in question)

    def action(self, entities, question):
        if(self.hasValidIntent(entities)):
            pass

