class BaseVoiceControllerModule:
    is_catchall = False

    def set_response_library(self, library):
        self.response = library

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        pass

    def contains_start_word(self, question):
        return any(command in question for command in ["enable", "turn on", "connect", "start"])

    def contains_stop_word(self, question):
        return any(command in question for command in ["disable", "turn off", "disconnect", "stop"])
