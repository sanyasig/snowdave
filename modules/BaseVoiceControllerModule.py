class BaseVoiceControllerModule:
    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        pass
