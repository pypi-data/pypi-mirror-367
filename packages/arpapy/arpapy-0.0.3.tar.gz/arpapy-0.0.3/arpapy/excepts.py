class PhonemeError(Exception):
    def __init__(self, message):
        self.message = message

class MissingLibrary(Exception):
    def __init__(self, message):
        self.message = message
