__version__ = '0.0.1'

from collections import namedtuple
from fuzzyfinder import fuzzyfinder
import importlib
import pkgutil
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import NestedCompleter, WordCompleter
from prompt_toolkit.shortcuts import set_title
from pyroute2 import IPRoute
import shlex
import socket

import rosh.commands
from rosh.commands import RoshCommand
from rosh.completer import link_completer


class Rosh():
    def __init__(self):
        set_title("rosh@{}".format(socket.getfqdn()))

        self.session = None
        self.ipr = IPRoute()
        self.commands = self.find_commands(rosh.commands)

        self.session = PromptSession(self.ps1,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=NestedCompleter.from_nested_dict(self.get_completers()),
                    complete_while_typing=True,
        )

        while True:
            try:
                text = self.session.prompt()
            except KeyboardInterrupt:
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D pressed.

            cmd = shlex.split(text)
            handler = self.get_command(*cmd)
            if handler is None:
                print("ERR: unknown command")
            else:
                handler(*cmd)

    @property
    def ipr(self):
        '''
        Get current IPRoute or NetNS instance for pyroute2 calls.
        '''
        return self._ipr
    
    @ipr.setter
    def ipr(self, value):
        '''
        Set current IPRoute or NetNS instance, updates the prompt
        and the reference in the link_completer, too 
        '''

        self._ipr = value
        link_completer.ipr = value

        if getattr(value, 'netns', None) is not None:
            self.set_prompt("{}#{}> ".format(socket.gethostname(), value.netns))
        else:
            self.set_prompt("{}> ".format(socket.gethostname()))

    def get_completers(self, commands=None):
        if commands is None:
            commands = self.commands

        d = {}
        for k, v in commands.items():
            if isinstance(v, RoshCommand):
                d[k] = v.completer
            elif isinstance(v, dict):
                d[k] = self.get_completers(v)
            else:
                d[k] = v

        return d

    def find_commands(self, ns_pkg):
        commands = {}
        strip = len(ns_pkg.__name__) + 1

        for finder, name, ispkg in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
            module = importlib.import_module(name)

            is_command = False
            try:
                is_command = module.is_rosh_command
            except AttributeError:
                pass

            childs = self.find_commands(module)

            if is_command:
                if childs:
                    commands[name[strip:]] = {
                        '': module.rosh_command(self)
                    }
                    commands[name[strip:]].update(childs)
                else:
                    commands[name[strip:]] = module.rosh_command(self)
            elif childs:
                commands[name[strip:]] = childs

        return commands

    def get_command(self, command, *args):
        def _get_cmd(commands, command='', *args):
            if command in commands:
                if isinstance(commands[command], dict):
                    return _get_cmd(commands[command], *args)
                elif isinstance(commands[command], RoshCommand):
                    return commands[command].handler
                else:
                    return commands[command]

        return _get_cmd(self.commands, command, *args)

    def set_prompt(self, prompt):
        self.ps1 = prompt
        if self.session is not None:
            self.session.message = prompt


def main():
    rosh = Rosh()

if __name__ == "__main__":
    main()
