class BaseVoiceControllerModule:
    is_catchall = False

    def set_response_library(self, library):
        self.response = library

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        pass
