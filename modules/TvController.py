from BaseVoiceControllerModule import BaseVoiceControllerModule


class TvController(BaseVoiceControllerModule):

    def should_action(self, keyword, entities):
       self.checkDoAction(entities, "tv")

    def action(self, entities, question):
        if(self.hasValidIntent(entities)):
            pass
