from abc import ABC, abstractmethod
import os.path
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

class RoshTuplesCommand(RoshCommand):
    def validate(self, cmd, args):
        (pos, msg, kwargs) = self.parse_args(cmd, args)

        return (pos, msg)

    def parse_args(self, cmd, args):
        if len(args) == 0:
            return (None, None, {})

        filters = []
        kwargs = {}

        for i in range(0, len(args), 2):
            if args[i] not in self.completer.tuples:
                return (i, 'invalid filter name', None)

            if args[i] in filters:
                return (i, f'filter "{args[i]}" already applied', None)

            filters.append(args[0])

            if i + 1 == len(args):
                return (i + 1, 'missing filter value', None)

            value_completer = self.completer.tuples[args[i]]
            if getattr(value_completer, 'base_completer', None):
                value_completer = value_completer.base_completer
            if callable(getattr(value_completer, 'parse_value', None)):
                try:
                    kwargs[args[i]] = value_completer.parse_value(self.rosh, args[i], args[i + 1])
                except ValueError as err:
                    return (i + 1, str(err), {})

        return (None, None, kwargs)

class RoshSystemCommand(RoshCommand):
    def __init__(self, rosh, exe, completer=None, env=None):
        super().__init__(rosh, completer)
        self.cmd = os.path.basename(exe)
        self.exe = exe
        self.env = env

    def handler(self, cmd, *args):
        print()

        if callable(self.env):
            env = self.env()
        else:
            env = self.env

        if getattr(self.rosh.ipr, 'netns', None):
            pyroute2.netns.pushns(self.rosh.ipr.netns)

        try:
            try:
                p = subprocess.Popen(
                    [self.cmd, *args],
                    executable=self.exe,
                    env=env)
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
