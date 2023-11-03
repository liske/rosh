from ipaddress import ip_address, ip_network
from socket import AF_INET6

from rosh.commands import RoshCommand
from rosh.completer import link_completer
from rosh.output import RoshOutputTable

class RoshShowIpv6RouteCommand(RoshCommand):
    def __init__(self, rosh):
        super().__init__(rosh, link_completer)
        self.family = AF_INET6

    def handler(self, cmd, *args):
        if len(args) == 0:
            self.handler_brief()
        elif len(args) == 1:
            self.handler_iface(args[0])

    def dump_route(self, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['dst', 'via', 'dev', 'prio', 'pref', 'proto', 'scope', 'flags']
        tbl.align['dst'] = 'l'
        tbl.align['via'] = 'l'
        tbl.align['ifname'] = 'l'
        tbl.sortby = 'dst'

        for route in self.rosh.ipr.get_routes(family=self.family, **filter):
            try:
                via = ip_address(route.get_attr('RTA_GATEWAY'))
            except ValueError:
                via = '-'

            tbl.add_row([
                ip_network(route.get_attr('RTA_DST', '::' if self.family == AF_INET6 else '0.0.0.0') + '/' + str(route['dst_len'])),
                via,
                route.get_attr('RTA_OIF'),
                route.get_attr('RTA_PRIORITY'),
                route.get_attr('RTA_PREF'),
                route['proto'],
                route['scope'],
                route['flags']
            ])
        print(tbl)

    def handler_brief(self):
        self.dump_route()

    def handler_iface(self, ifname):
        self.dump_route(ifname=ifname)

    def validate(self, cmd, args):
        if len(args) > 1:
            return (1, "to many parameters (>1)")

        if len(args) == 1 and not args[0] in link_completer.get_links():
            return (0, f"{args[0]} does not exist")

        return (None, None)


is_rosh_command = True
rosh_command = RoshShowIpv6RouteCommand
