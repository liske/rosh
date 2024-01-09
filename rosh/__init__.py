__version__ = '0.1.7'

import argparse
from cachetools import cached, TTLCache
import configparser
from fuzzyfinder import fuzzyfinder
import importlib
import os
import pkgutil
import platform
from prompt_toolkit import PromptSession, print_formatted_text as print
from prompt_toolkit.application.current import get_app_session
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import NestedCompleter, WordCompleter, DummyCompleter, merge_completers
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.shortcuts import set_title, CompleteStyle
from prompt_toolkit.styles import Style
from pyroute2 import IPRoute, netns
from setproctitle import setproctitle
import shlex
import socket
import sys
from types import SimpleNamespace

import rosh.commands
from rosh.commands import RoshCommand
from rosh.completer import link_completer, netns_completer, phy_link_completer, RoshPeerCompleter, RoshTuplesCompleter
from rosh.filters import RoshFilter
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
    def __init__(self, config_file):
        set_title("rosh@{}".format(socket.getfqdn()))

        self.session = None
        self.quit_callbacks = []

        # initialize default config
        self.config = configparser.ConfigParser()
        self.config['prompt'] = {
            'complete_while_typing': True,
            'complete_style': 'READLINE_LIKE',
            'reserve_space_for_menu': -1,
        }

        self.commands = self.find_commands(rosh.commands)
        self.filters = self.find_filters(rosh.filters)
        self.configure(config_file)

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
                    complete_while_typing=self.config.getboolean('prompt', 'complete_while_typing'),
                    complete_style=self.config['prompt']['complete_style'],
                    reserve_space_for_menu=self.config.getint('prompt', 'reserve_space_for_menu'),
                    style=self.style,
                    validator=RoshValidator(self),
                    validate_while_typing=False,
        )

        self.print_banner()


    def configure(self, config_file):
        '''
        Load user configuration from file.
        '''

        # read user config
        self.config.read(config_file)

        # sanity checks & auto settings
        complete_style = self.config['prompt']['complete_style']
        if not complete_style in ['COLUMN', 'MULTI_COLUMN', 'READLINE_LIKE']:
            complete_style = 'COLUMN'
            self.config['prompt']['complete_style'] = complete_style

        reserve_space_for_menu = self.config.getint('prompt', 'reserve_space_for_menu')
        if reserve_space_for_menu == -1:
            if complete_style == 'READLINE_LIKE':
                reserve_space_for_menu = 0
            else:
                reserve_space_for_menu = 4
            self.config['prompt']['reserve_space_for_menu'] = str(reserve_space_for_menu)


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

    def parse_filters(self, cmd):
        filters = []

        # get filters if there is a pipe symbol
        if '|' in cmd:
            # split cmd by pipe symbol
            while '|' in cmd:
                idx = cmd.index('|')
                filters.append(cmd[:idx])
                cmd = cmd[idx+1:]
            filters.append(cmd)

            # shift first filter, this is the cmd
            cmd = filters.pop(0)

        return (cmd, filters)

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

            # split command line by pipe symbols
            (cmd, flts) = self.parse_filters(cmd)

            # skip when there is no command
            if len(cmd) == 0:
                continue

            # get command
            (depth, command, cmd_arg0, cmd_args) = self.get_command(*cmd)
            if not command:
                print("ERR: unknown command")
                continue

            # get filters
            filters_ok = True
            filters = None
            for flt in flts:
                (filt, flt_arg0, flt_args) = self.get_filter(*flt)
                if not filt:
                    print("ERR: unknown filter")
                    filters_ok = False
                    break

                if filters is None:
                    filters = []

                filters.append(filt(self, flt_arg0, *flt_args))

            if not filters_ok:
                continue

            command.handler(filters, cmd_arg0, *cmd_args)

        for cb in self.quit_callbacks:
            cb()

    def dump_commands(self, filters=None):
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
                if isinstance(val, RoshCommand) or isinstance(val, RoshFilter):
                    description = getattr(val, 'description', '')

                    lines = [
                        "{}{}".format(
                            "{}{}".format(''.ljust(indent), cmd).ljust(18),
                            description
                        )
                    ]
                    if val.completer is not None:
                        descriptions = _get_description(val.completer)
                        if descriptions:
                            description = ' '.join(descriptions)
                            lines.append("{}  {}".format(''.ljust(indent), description))
                    if RoshFilter.filter_test_list(filters, lines):
                        for line in lines:
                            print(line)
                else:
                    line = "{}{}".format(''.ljust(indent), cmd)
                    if RoshFilter.filter_test_item(filters, line):
                        print(line)
                        _dump(indent+2, val)

        print("available commands:")
        _dump(2, self.commands)

        print()
        print("available filters:")
        for filt, flt in sorted(self.filters.items()):
            description = getattr(flt, 'description', '')

            line = "{}{}".format(
                "  {}".format(filt).ljust(18),
                description
            )

            if RoshFilter.filter_test_item(filters, line):
                print(line)

    def dump_config(self):
        '''
        Prints the parsed configuration values.
        '''
        self.config.write(sys.stdout)

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
        phy_link_completer.ipr = value

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

    def get_completers(self, commands=None, filter_completers=None):
        '''
        Extracts the completers from commands dict.
        '''
        if commands is None:
            commands = self.commands

        if filter_completers is None:
            filter_completers = NestedCompleter({
                        '': DummyCompleter(),
                        '|': self.get_filter_completers()
            })

        d = {}
        for k, v in commands.items():
            if isinstance(v, RoshCommand):
                c = v.completer
                if c is None:
                    d[k] = filter_completers
                else:
                    d[k] = c
            elif isinstance(v, dict):
                d[k] = self.get_completers(v, filter_completers)

        return d

    def get_filter_completers(self):
        '''
        Extracts the completers from filters list.
        '''

        nc = NestedCompleter({})

        d = {}
        for k, v in self.filters.items():
            d[k] = RoshPeerCompleter(
                v.completer,
                NestedCompleter({
                    '': DummyCompleter(),
                    '|': nc
                }))
        nc.options = d

        return nc

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
        def _abbrev_cmd(commands):
            abbreviations = {}
            for command in commands.keys():
                for i in range(1, len(command)):
                    cmd = command[:i]
                    if len(list(filter(lambda x: x.startswith(cmd), commands))) == 1:
                        abbreviations[cmd] = commands[command]
            return abbreviations

        def _get_cmd(depth, commands, command='', *args):
            if command in commands:
                if isinstance(commands[command], dict):
                    return _get_cmd(depth + 1, commands[command], *args)
                elif isinstance(commands[command], RoshCommand):
                    return (depth, commands[command], command, args)
            else:
                abbreviations = _abbrev_cmd(commands)
                if command in abbreviations:
                    if isinstance(abbreviations[command], dict):
                        return _get_cmd(depth + 1, abbreviations[command], *args)
                    elif isinstance(abbreviations[command], RoshCommand):
                        return (depth, abbreviations[command], command, args)

            return (depth, None, command, args)

        return _get_cmd(1, self.commands, command, *args)

    def find_filters(self, ns_pkg):
        '''
        Finds packages in a namespace which have a `is_filter`
        attribute set to `True`, recursively.
        '''
        filters = {}
        strip = len(ns_pkg.__name__) + 1

        for finder, name, ispkg in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
            module = importlib.import_module(name)

            is_filter = False
            try:
                is_filter = module.is_rosh_filter
            except AttributeError:
                pass

            childs = self.find_filters(module)

            if is_filter:
                if childs:
                    filters[name[strip:]] = {
                        '': module.rosh_filter
                    }
                    filters[name[strip:]].update(childs)
                else:
                    filters[name[strip:]] = module.rosh_filter
            elif childs:
                filters[name[strip:]] = childs

        return filters

    def get_filter(self, filt, *args):
        '''
        Searches the flat internal filters dict searching for the
        filter and returns a tuple:
        - the RoshFilter that matched (or None)
        - the filter name that matched
        - additional filter parameters
        '''
        def _abbrev_flt():
            abbreviations = {}
            for filt in self.filters.keys():
                for i in range(1, len(filt)):
                    flt = filt[:i]
                    if len(list(filter(lambda x: x.startswith(flt), self.filters))) == 1:
                        abbreviations[flt] = self.filters[filt]
            return abbreviations

        if filt in self.filters:
            return (self.filters[filt], filt, args)
        else:
            abbreviations = _abbrev_flt()
            if filt in abbreviations:
                return (abbreviations[filt], filt, args)

        return (None, filt, args)

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

    def register_quit_fn(self, cb):
        '''
        Register a callback function to be called before rosh terminates.
        '''
        self.quit_callbacks.append(cb)

def main():
    # update proc title
    setproctitle(sys.argv[0])

    # prepare argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('-c', dest='config', default='/etc/rosh.conf', required=False, help='configuration filename')

    subparsers = parser.add_subparsers(
        dest='action', required=False, help="specifies the action to perform")

    action_parsers = {
        'commands': subparsers.add_parser('commands', help='dump available commands'),
        'config': subparsers.add_parser('config', help='dump parsed configuration'),
        'shell': subparsers.add_parser('shell', help='run interactive shell (default)'),
    }

    args = parser.parse_args()
    action = args.action or 'shell'

    assert action in action_parsers

    rosh = Rosh(args.config)
    if action == 'shell':
        rosh.prompt_loop()
    elif action == 'commands':
        rosh.dump_commands()
    elif action == 'config':
        rosh.dump_config()

if __name__ == "__main__":
    main()
