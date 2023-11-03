from abc import ABC, abstractmethod

from rosh.output import RoshOutputDict

class RoshCommand():
    def __init__(self, rosh, completer=None):
        self.rosh = rosh
        self.completer = completer
        self.print = RoshOutputDict().print

    @abstractmethod
    def handler(self, cmd, *args):
        pass
