from ipaddress import IPv4Address, IPv6Address, ip_address, ip_network
from prompt_toolkit.completion import NestedCompleter, WordCompleter, DummyCompleter
from socket import AF_INET6

from rosh.commands import RoshTuplesCommand
from rosh.completer import link_completer, proto_completer, scope_completer, table_completer, RoshTuplesCompleter, RoshIpCompleter, RoshPfxCompleter
from rosh.output import RoshOutputTable
from rosh.rtlookup import protos, scopes

class RoshShowIpv6RouteCommand(RoshTuplesCommand):
    description = 'show ipv6 routes'

    def __init__(self, rosh, family=AF_INET6):
        self.family = family

        completer = RoshTuplesCompleter({
            'dst': RoshPfxCompleter(family),
            'oif': link_completer,
            'gateway': RoshIpCompleter(family),
            'proto': proto_completer,
            'scope': scope_completer,
            'table': table_completer,
        })

        super().__init__(rosh, completer)

    def handler(self, filters, cmd, *args):
        (pos, msg, kwargs) = self.parse_args(cmd, args)

        assert pos is None

        self.dump_route(**kwargs)

    def dump_route(self, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['dst', 'gw', 'oif', 'prio', 'pref', 'proto', 'scope', 'flags']
        tbl.align['dst'] = 'l'
        tbl.align['gw'] = 'l'
        tbl.align['oif'] = 'l'
        tbl.sortby = 'dst'

        for route in self.rosh.ipr.get_routes(family=self.family, **filter):
            try:
                via = str(ip_address(route.get_attr('RTA_GATEWAY')))
            except ValueError:
                via = '-'

            tbl.add_row([
                str(ip_network(route.get_attr('RTA_DST', '::' if self.family == AF_INET6 else '0.0.0.0') + '/' + str(route['dst_len']))),
                via,
                self.rosh.idx_to_ifname(route.get_attr('RTA_OIF')),
                route.get_attr('RTA_PRIORITY', '-'),
                route.get_attr('RTA_PREF', '-'),
                protos.lookup_str(route['proto']),
                scopes.lookup_str(route['scope']),
                route['flags']
            ])
        print(tbl)


is_rosh_command = True
rosh_command = RoshShowIpv6RouteCommand
