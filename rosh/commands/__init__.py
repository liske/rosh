from abc import ABC, abstractmethod
import pyroute2.netns
import subprocess

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

class RoshSystemCommand(RoshCommand):
    def __init__(self, rosh, cmd):
        super().__init__(rosh)
        self.cmd = cmd

    def handler(self, cmd, *args):
        print()

        if getattr(self.rosh.ipr, 'netns', None):
            pyroute2.netns.pushns(self.rosh.ipr.netns)

        try:
            try:
                p = subprocess.Popen([self.cmd, *args])
                p.wait()
            except KeyboardInterrupt:
                p.terminate()
                p.wait()
        finally:
            if getattr(self.rosh.ipr, 'netns', None):
                pyroute2.netns.popns()
        print()

    @abstractmethod
    def validate(self, cmd, args):
        return (None, None)
