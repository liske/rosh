from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network
from prompt_toolkit.completion import NestedCompleter
from socket import AF_INET6

from rosh.commands import RoshCommand
from rosh.completer import link_completer
from rosh.output import RoshOutputTable
from rosh.rtlookup import protos, scopes

class RoshShowIpv6RouteCommand(RoshCommand):
    def __init__(self, rosh):
        self.commands = {
            '': None,
            'dev': link_completer,
            'via': None,
        }
        super().__init__(rosh, NestedCompleter.from_nested_dict(self.commands))
        self.family = AF_INET6

    def handler(self, cmd, *args):
        (pos, msg, kwargs) = self.parse_args(cmd, args)

        assert pos is None

        self.dump_route(**kwargs)

    def dump_route(self, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['dst', 'via', 'dev', 'prio', 'pref', 'proto', 'scope', 'flags']
        tbl.align['dst'] = 'l'
        tbl.align['via'] = 'l'
        tbl.align['dev'] = 'l'
        tbl.sortby = 'dst'

        for route in self.rosh.ipr.get_routes(family=self.family, **filter):
            try:
                via = ip_address(route.get_attr('RTA_GATEWAY'))
            except ValueError:
                via = '-'

            tbl.add_row([
                ip_network(route.get_attr('RTA_DST', '::' if self.family == AF_INET6 else '0.0.0.0') + '/' + str(route['dst_len'])),
                via,
                self.rosh.idx_to_ifname(route.get_attr('RTA_OIF')),
                route.get_attr('RTA_PRIORITY', '-'),
                route.get_attr('RTA_PREF', '-'),
                protos.lookup_str(route['proto']),
                scopes.lookup_str(route['scope']),
                route['flags']
            ])
        print(tbl)

    def validate(self, cmd, args):
        (pos, msg, kwargs) = self.parse_args(cmd, args)

        return (pos, msg)

    def parse_args(self, cmd, args):
        if len(args) == 0:
            return (None, None, {})

        filters = []
        kwargs = {}

        for i in range(0, len(args), 2):
            if args[i] not in self.commands:
                return (i, 'invalid filter name', None)

            if args[i] in filters:
                return (i, f'filter "{args[i]}" already applied', None)

            filters.append(args[0])

            if i + 1 == len(args):
                return (i + 1, 'missing filter value', None)

            if args[i] == 'dev':
                if args[i + 1] not in link_completer.get_links():
                    return (i + 1, f'interface "{args[i + 1]}" does not exist', None)
                kwargs['oif'] = self.rosh.ifname_to_idx(args[i + 1])
            elif args[i] == 'via':
                try:
                    if self.family == AF_INET6:
                        kwargs['gateway'] = IPv6Address(args[i + 1])
                    else:
                        kwargs['gateway'] = IPv4Address(args[i + 1])
                except ValueError as err:
                    return (i + 1, str(err))

        return (None, None, kwargs)


is_rosh_command = True
rosh_command = RoshShowIpv6RouteCommand
