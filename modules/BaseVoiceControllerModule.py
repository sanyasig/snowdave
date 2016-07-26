import unicodedata


class BaseVoiceControllerModule:
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



