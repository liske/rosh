from abc import ABC, abstractmethod

from rosh.output import RoshOutputDetails

class RoshCommand():
    def __init__(self, rosh, completer=None):
        self.rosh = rosh
        self.completer = completer
        self.output = RoshOutputDetails()

    @abstractmethod
    def handler(self, cmd, *args):
        pass

    @abstractmethod
    def validate(self, cmd, args):
        return (None, None)
