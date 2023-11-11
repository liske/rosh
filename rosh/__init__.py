__version__ = '0.1.1'

import argparse
from cachetools import cached, TTLCache
from fuzzyfinder import fuzzyfinder
import importlib
import os
import pkgutil
import platform
from prompt_toolkit import PromptSession, print_formatted_text as print
from prompt_toolkit.application.current import get_app_session
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter, WordCompleter
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import set_title
from prompt_toolkit.styles import Style
from pyroute2 import IPRoute, netns
from setproctitle import setproctitle
import shlex
import socket
import sys
from types import SimpleNamespace

import rosh.commands
from rosh.commands import RoshCommand
from rosh.completer import link_completer, netns_completer, RoshPeerCompleter, RoshTuplesCompleter
from rosh.validator import RoshValidator

# terminal with restricted color and font support (linux, xterm, vt100)
BASE_STYLE = Style.from_dict({
    '':              '',
    'host':          'ansiwhite bg:ansigreen',
    'host_end':      'ansigreen',
    'host_netns':    'ansigreen bg:ansiyellow',
    'netns':         'ansiblack bg:ansiyellow bold',
    'netns_begin':   'bg:ansiyellow',
    'netns_end':     'ansiyellow',
})
BASE_SYMBOLS = SimpleNamespace(router='●', netns='▢', delimiter='◤')

# modern terminals (default)
EXTENDED_STYLE = Style.from_dict({
    '':              '',
    'host':          '#aadd00 bg:#209680',
    'host_end':      '#209680',
    'host_netns':    '#209680 bg:#aadd00',
    'netns':         '#209680 bg:#aadd00 bold',
    'netns_begin':   'bg:#aadd00',
    'netns_end':     '#aadd00',
})
EXTENDED_SYMBOLS = SimpleNamespace(router='⬤', netns='▢', delimiter='◤')

class Rosh():
    '''
    This is the main class of RoSh providing the prompt-toolkit
    PromptSession.
    '''
    def __init__(self):
        set_title("rosh@{}".format(socket.getfqdn()))

        self.session = None
        self.commands = self.find_commands(rosh.commands)

        if os.environ.get('TERM') in ['linux', 'xterm', 'vt100']:
            self.style = BASE_STYLE
            self.symbols = BASE_SYMBOLS
        else:
            self.style = EXTENDED_STYLE
            self.symbols = EXTENDED_SYMBOLS

        self.ipr = IPRoute()
        self.session = PromptSession(self.ps1,
                    auto_suggest=AutoSuggestFromHistory(),
                    completer=NestedCompleter.from_nested_dict(self.get_completers()),
                    complete_while_typing=True,
                    reserve_space_for_menu=2,
                    style=self.style,
                    validator=RoshValidator(self),
                    validate_while_typing=False,
        )

        self.print_banner()

    def print_banner(self):
        '''
        Print startup shell banner.
        '''
        uname = platform.uname()

        lines = [
            ('bold', f'{uname.system} {uname.node} {uname.release}'),
            ('', f'Router Shell {__version__}'),
        ]
        size = get_app_session().output.get_size()

        print()
        for line in lines:
            text = FormattedText([(line[0], line[1].center(size.columns))])
            print(text, style=self.style)
        print()

        self.print_netns_brief()

    def print_netns_brief(self):
        '''
        Print a brief list of NetNS on startup (if allowed).
        '''
        try:
            items = []
            length = 0
            for ns in sorted(netns.listnetns()):
                items.append(FormattedText([
                    ('class:netns', f' {self.symbols.netns} {ns} '),
                    ('class:netns_end', self.symbols.delimiter),
                ]))
                length += len(ns) + 5
        except PermissionError:
            return

        if len(items) == 0:
            return

        size = get_app_session().output.get_size()

        print(' '.ljust(int((size.columns - length)/2) - len(items)), end='')
        for text in items:
            print(' ', text, style=self.style, end='')
        print()
        print()

    def prompt_loop(self):
        '''
        Main REPL loop, will never return.
        '''
        while True:
            try:
                text = self.session.prompt()
            except KeyboardInterrupt:
                continue  # Control-C pressed. Try again.
            except EOFError:
                break  # Control-D pressed.

            cmd = shlex.split(text)

            # skip empty input
            if len(cmd) == 0:
                continue

            (depth, command, arg0, args) = self.get_command(*cmd)
            if not command:
                print("ERR: unknown command")
            else:
                command.handler(arg0, *args)

    def dump_commands(self):
        '''
        Prints the available command hierarchy to the terminal.
        '''
        def _get_description(completer):
            description = getattr(completer, 'description', None)
            if description is None:
                if isinstance(completer, WordCompleter):
                    words = completer.words
                    if callable(words):
                        words = words()
                    if '' in words:
                        return ['[{}]'.format('|'.join([w for w in words if w != '']))]
                    else:
                        return ['<{}>'.format('|'.join(words))]
                elif isinstance(completer, RoshPeerCompleter):
                    return _get_description(completer.base_completer) + _get_description(completer.sub_completer)
                elif isinstance(completer, RoshTuplesCompleter):
                    descriptions = []
                    for key, val in sorted(completer.flat_tuples.items(), key=lambda x: x[0]):
                        descriptions.append(f'[{key} <{"|".join(_get_description(val))}>]')
                    return descriptions
            else:
                return [description]

            return []

        def _dump(indent, commands):
            for cmd, val in sorted(commands.items(), key=lambda x: x[0]):
                if isinstance(val, RoshCommand):
                    description = getattr(val, 'description', '')
                    print("{}{}".format(''.ljust(indent), cmd).ljust(18), description)
                    if val.completer is not None:
                        descriptions = _get_description(val.completer)
                        if descriptions:
                            description = ' '.join(descriptions)
                            print("{}  {}".format(''.ljust(indent), description))
                else:
                    print("{}{}".format(''.ljust(indent), cmd))
                    _dump(indent+2, val)

        print("available commands:")
        _dump(0, self.commands)

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

        # clear lookup cache
        self.cache_idx_to_ifname = TTLCache(maxsize=32, ttl=20)
        self.cache_ifname_to_idx = TTLCache(maxsize=32, ttl=20)

        link_completer.ipr = value

        hostname = socket.gethostname() or localhost

        if getattr(value, 'netns', None) is not None:
            self.set_prompt([
                ('class:host', f' {self.symbols.router} {hostname} '),
                ('class:host_netns', f'{self.symbols.delimiter}'),
                ('class:netns', f'{self.symbols.netns} {value.netns} '),
                ('class:netns_end', f'{self.symbols.delimiter}'),
                ('', ' '),
            ])
        else:
            self.set_prompt([
                ('class:host', f' {self.symbols.router} {hostname} '),
                ('class:host_end', f'{self.symbols.delimiter}'),
                ('', ' '),
            ])

    def get_completers(self, commands=None):
        '''
        Extracts the completers from commands dict.
        '''
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
        '''
        Finds packages in a namespace which have a `is_rosh_command`
        attribute set to `True`, recursively.
        '''
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
        '''
        Traverses the internal commands dict searching for the command
        and returns a tuple:
        - the depth where the command has matched (if any)
        - the RoshCommand that matched (or None)
        - the command name that matched
        - additional command parameters
        '''
        def _get_cmd(depth, commands, command='', *args):
            if command in commands:
                if isinstance(commands[command], dict):
                    return _get_cmd(depth + 1, commands[command], *args)
                elif isinstance(commands[command], RoshCommand):
                    return (depth, commands[command], command, args)

            return (depth, None, command, args)

        return _get_cmd(1, self.commands, command, *args)

    def set_prompt(self, prompt):
        '''
        Updates the prompt prefix.
        '''
        self.ps1 = prompt
        if self.session is not None:
            self.session.message = prompt

    def idx_to_ifname(self, idx):
        '''
        Converts an ifindex into a ifname (returns ifindex if the name
        cannot be resolved).

        The lookup is cached for 20s.
        '''
        # cache lookup
        ifname = self.cache_idx_to_ifname.get(idx)
        if ifname is not None:
            return ifname

        link = next(iter(self.ipr.get_links(index=idx)), None)

        if link is None:
            ifname = idx
        else:
            ifname = link.get_attr('IFLA_IFNAME', idx)

        self.cache_idx_to_ifname[idx] = ifname

        return ifname

    def ifname_to_idx(self, ifname):
        '''
        Converts an ifname into a ifindex (returns 0 if the name
        cannot be resolved).

        The lookup is cached for 20s.
        '''
        # cache lookup
        idx = self.cache_ifname_to_idx.get(ifname)
        if idx is not None:
            return idx

        link = next(iter(self.ipr.get_links(ifname=ifname)), None)

        if link is None:
            idx = 0
        else:
            idx = link['index']

        self.cache_ifname_to_idx[ifname] = idx

        return idx

def main():
    # update proc title
    setproctitle(sys.argv[0])

    # prepare argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))

    subparsers = parser.add_subparsers(
        dest='action', required=False, help="specifies the action to perform")

    action_parsers = {
        'shell': subparsers.add_parser('shell', help='run interactive shell (default)'),
        'commands': subparsers.add_parser('commands', help='dump available commands'),
    }

    args = parser.parse_args()
    action = args.action or 'shell'

    assert action in action_parsers

    rosh = Rosh()
    if action == 'shell':
        rosh.prompt_loop()
    elif action == 'commands':
        rosh.dump_commands()

if __name__ == "__main__":
    main()
