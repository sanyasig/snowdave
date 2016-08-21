class BaseVoiceControllerModule:
    is_catchall = False

    def set_response_library(self, library):
        self.response = library

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        pass

    def contains_start_word(self, question):
        return "enable" in question or "turn on" in question or "connect" in question or "start" in question

    def contains_stop_word(self, question):
        return "disable" in question or "turn off" in question or "disconnect" in question or "stop" in question
