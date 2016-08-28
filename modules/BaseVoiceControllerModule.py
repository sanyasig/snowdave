class BaseVoiceControllerModule:
    is_catchall = False

    def set_response_library(self, library):
        self.response = library

    def set_config(self, config_json):
        self.config = config_json

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        pass

    def is_my_intent(self, witai, intent):
        return witai and "intent" in witai["entities"] and len(witai["entities"]["intent"]) > 0 and intent == witai["entities"]["intent"][0]["value"].strip()

    def get_action(self, witai):
        if "action" in witai["entities"] and len(witai["entities"]["action"]) > 0:
            return witai["entities"]["action"][0]["value"].strip()
        return None

    def contains_start_word(self, question):
        return any(command in question for command in ["enable", "turn on", "connect", "start"])

    def contains_stop_word(self, question):
        return any(command in question for command in ["disable", "turn off", "disconnect", "stop"])
