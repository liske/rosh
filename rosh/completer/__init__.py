from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network
from prompt_toolkit.completion import Completer, DummyCompleter, WordCompleter
from prompt_toolkit.document import Document
from pyroute2 import netns, IPRoute
import shlex
from socket import AF_INET, AF_INET6

from rosh.commands import RoshCommand
from rosh.lookup import neigh_flags, neigh_states, ifa_flags
from rosh.rtlookup import protos, realms, tables, scopes


class RoshPeerCompleter(Completer):
    def __init__(self, base_completer, sub_completer):
        self.base_completer = base_completer
        self.sub_completer = sub_completer

    def get_completions(self, document, complete_event):
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # if there is a space and use the subcompleter.
        if " " in text:
            first_term = text.split()[0]
            remaining_text = text[len(first_term) :].lstrip()
            move_cursor = len(text) - len(remaining_text) + stripped_len

            new_document = Document(
                remaining_text,
                cursor_position=document.cursor_position - move_cursor,
            )

            yield from self.sub_completer.get_completions(new_document, complete_event)

        # no space in the input: use the base completer
        else:
            yield from self.base_completer.get_completions(document, complete_event)

class RoshTuplesCompleter(Completer):
    def __init__(self, tuples):
        self.tuples = {}

        # build recursive completer
        for keyword, completer in tuples.items():
            # get tuples not completed, yet
            other_tuples = tuples.copy()
            del other_tuples[keyword]

            # chain current completer with completers of remaining tuples
            self.tuples[keyword] = RoshPeerCompleter(
                completer,
                RoshTuplesCompleter(other_tuples)
            )

        # keyword completer
        self.keywords_completer = WordCompleter(sorted(tuples.keys()))

    def get_completions(self, document, complete_event):
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # if there is a space and use a subcompleter, if available
        if " " in text:
            first_term = text.split()[0]
            if first_term in self.tuples:
                remaining_text = text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                yield from self.tuples[first_term].get_completions(new_document, complete_event)
            else:
                return []
        # no space in the input: use the base completer
        else:
            yield from self.keywords_completer.get_completions(document, complete_event)

class RoshWordCompleter(WordCompleter):
    def parse_value(self, rosh, name, value):
        words = self.words
        if callable(words):
            words = words()

        if value not in words:
            if getattr(self, 'description', None) is not None:
                raise ValueError(f'{value} is invalid for {self.description}')
            else:
                raise ValueError(f'{value} is a invalid value')

        lookup_id = getattr(self, 'lookup_id', None)
        if callable(lookup_id):
            return lookup_id(rosh, value)

        return value

class RoshLinkCompleter(RoshWordCompleter):
    description = '{ifname}'

    def __init__(self):
        self.ipr = None
        super().__init__(self.get_links)

    def set_ipr(self, ipr):
        self.ipr = ipr

    def get_links(self):
        links = []
        if self.ipr is not None:
            for link in sorted(self.ipr.get_links(), key=lambda x: x.get_attr('IFLA_IFNAME', x['index'])):
                links.append(shlex.quote(link.get_attr('IFLA_IFNAME')))
        return links

    def lookup_id(self, rosh, ifname):
        return rosh.ifname_to_idx(ifname)

class RoshNetNSCompleter(RoshWordCompleter):
    description = '{netns}'

    def __init__(self):
        super().__init__(self.get_netns)

    def get_netns(self):
        l = []
        for ns in sorted(netns.listnetns()):
            l.append(shlex.quote(ns))
        return l

class RoshProtoCompleter(RoshWordCompleter):
    description = '{proto}'

    def __init__(self):
        super().__init__(self.get_protos)

    def get_protos(self):
        return sorted(protos.str2id.keys())

    def lookup_id(self, rosh, proto):
        return protos.lookup_id(proto)

class RoshRealmCompleter(RoshWordCompleter):
    description = '{realm}'

    def __init__(self):
        super().__init__(self.get_realms)

    def get_realms(self):
        return sorted(realms.str2id.keys())

    def lookup_id(self, rosh, realm):
        return realms.lookup_id(realm)

class RoshScopeCompleter(RoshWordCompleter):
    description = '{scope}'

    def __init__(self):
        super().__init__(self.get_scopes)

    def get_scopes(self):
        return sorted(scopes.str2id.keys())

    def lookup_id(self, rosh, scope):
        return scopes.lookup_id(scope)

class RoshTableCompleter(RoshWordCompleter):
    description = '{table}'

    def __init__(self):
        super().__init__(self.get_tables)

    def get_tables(self):
        return sorted(tables.str2id.keys())

    def lookup_id(self, rosh, table):
        return tables.lookup_id(table)

class RoshIpv4Completer(DummyCompleter):
    description = '{ip}'

    def parse_value(self, rosh, name, value):
        return str(IPv4Address(value))

class RoshIpv6Completer(DummyCompleter):
    description = '{ipv6}'

    def parse_value(self, rosh, name, value):
        return str(IPv6Address(value))

class RoshIpCompleter():
    def __new__(cls, *args, **kwargs):
        if AF_INET in args:
            return super().__new__(RoshIpv4Completer)

        return super().__new__(RoshIpv6Completer)

class RoshPfxv4Completer(DummyCompleter):
    description = '{pfx}'

    def parse_value(self, rosh, name, value):
        return str(IPv4Network(value))

class RoshPfxv6Completer(DummyCompleter):
    description = '{pfxv6}'

    def parse_value(self, rosh, name, value):
        return str(IPv6Network(value))

class RoshPfxCompleter():
    def __new__(cls, *args, **kwargs):
        if AF_INET in args:
            return super().__new__(RoshPfxv4Completer)

        return super().__new__(RoshPfxv6Completer)

class RoshNeighFlagCompleter(RoshWordCompleter):
    description = '{flags}'

    def __init__(self):
        super().__init__(sorted(neigh_flags.str2id.keys()))

    def lookup_id(self, rosh, flags):
        return neigh_flags.lookup_id(flags)

class RoshNeighStateCompleter(RoshWordCompleter):
    description = '{state}'

    def __init__(self):
        super().__init__(sorted(neigh_states.str2id.keys()))

    def lookup_id(self, rosh, state):
        return neigh_states.lookup_id(state)

class RoshIfaFlagCompleter(RoshWordCompleter):
    description = '{flag}'

    def __init__(self):
        super().__init__(sorted(ifa_flags.str2id.keys()))

    def lookup_id(self, rosh, flag):
        return ifa_flags.lookup_id(flag)


link_completer = RoshLinkCompleter()
netns_completer = RoshNetNSCompleter()
proto_completer = RoshProtoCompleter()
realm_completer = RoshRealmCompleter()
table_completer = RoshTableCompleter()
scope_completer = RoshScopeCompleter()
neighflag_completer = RoshNeighFlagCompleter()
neighstate_completer = RoshNeighStateCompleter()
