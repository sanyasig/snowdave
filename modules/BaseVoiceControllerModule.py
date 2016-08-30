class BaseVoiceControllerModule:
    is_catchall = False

    def set_response_library(self, library):
        self.response = library

    def set_config(self, config_json):
        self.config = config_json

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        raise Exception("I need overwriting")

    def is_my_intent(self, witai, intent):
        return self.get_witai_item(witai, "intent") == intent

    def is_my_action(self, witai, action):
        return self.get_witai_item(witai, "action") == action

    def get_witai_item(self, witai, item):
        return witai["entities"][item][0]["value"].strip() if item in witai["entities"] and len(witai["entities"][item]) > 0 else None

    def contains_start_word(self, question):
        return any(command in question for command in ["enable", "turn on", "connect", "start"])

    def contains_stop_word(self, question):
        return any(command in question for command in ["disable", "turn off", "disconnect", "stop"])
