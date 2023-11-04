from ipaddress import ip_interface

from socket import AF_INET6

from rosh.commands import RoshCommand
from rosh.completer import link_completer
from rosh.rtlookup import scopes
from rosh.output import RoshOutputTable


class RoshShowIpv6AddressCommand(RoshCommand):
    description = 'show assigned ipv6 addresses'

    def __init__(self, rosh):
        super().__init__(rosh, link_completer)
        self.family = AF_INET6

    def handler(self, cmd, *args):
        if len(args) == 0:
            self.handler_brief()
        elif len(args) == 1:
            self.handler_iface(args[0])

    def dump_addr(self, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['address', 'ifname', 'scope', 'flags']
        tbl.align['address'] = 'l'
        tbl.align['ifname'] = 'l'
        tbl.sortby = 'address'

        for addr in self.rosh.ipr.get_addr(family=self.family, **filter):
            tbl.add_row([
                ip_interface(addr.get_attr('IFA_ADDRESS') + '/' + str(addr['prefixlen'])),
                self.rosh.idx_to_ifname(addr['index']),
                scopes.lookup_str(addr['scope']),
                addr['flags']
            ])
        print(tbl)

    def handler_brief(self):
        self.dump_addr()

    def handler_iface(self, ifname):
        self.dump_addr(ifname=ifname)

    def validate(self, cmd, args):
        if len(args) > 1:
            return (1, "to many parameters (>1)")

        if len(args) == 1 and not args[0] in link_completer.get_links():
            return (0, f"{args[0]} does not exist")

        return (None, None)


is_rosh_command = True
rosh_command = RoshShowIpv6AddressCommand
