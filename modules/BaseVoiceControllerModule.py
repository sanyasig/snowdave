import unicodedata


class BaseVoiceControllerModule:
    is_catchall = False

    def set_response_library(self, library):
        self.response = library

    def should_action(self, keyword, question):
        return False

    def action(self, keyword, question):
        pass

    def convertUnicode(self, value):
        return unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')

    def hasValidIntent(self, entities):
        returnValue = False
        if ("intent" in entities):
            returnValue = entities["intent"][0]["confidence"] > 0.96
        return returnValue

    def checkDoAction(self, entities, stringToLook):
        returnValue = False
        if self.hasValidIntent(entities):
            intent = self.convertUnicode(entities["intent"][0]["value"])
            returnValue = stringToLook in intent
        return returnValue

    def is_my_intent(self, witai, intent):
        return witai and "intent" in witai["entities"] and len(witai["entities"]["intent"]) > 0 and intent == \
                                                                                                    witai["entities"][
                                                                                                        "intent"][0][
                                                                                                        "value"].strip()

    def get_action(self, witai):
        if "action" in witai["entities"] and len(witai["entities"]["action"]) > 0:
            return witai["entities"]["action"][0]["value"].strip()
        return None

    def contains_start_word(self, question):
        return any(command in question for command in ["enable", "turn on", "connect", "start"])

    def contains_stop_word(self, question):
        return any(command in question for command in ["disable", "turn off", "disconnect", "stop"])





