from ipaddress import ip_interface

from socket import AF_INET6

from rosh.commands import RoshTuplesCommand
from rosh.completer import link_completer, RoshTuplesCompleter
from rosh.lookup import ifa_flags
from rosh.rtlookup import scopes
from rosh.output import RoshOutputTable


class RoshShowIpv6AddressCommand(RoshTuplesCommand):
    description = 'show assigned ipv6 addresses'

    def __init__(self, rosh, family=AF_INET6):
        self.family = family

        completer = RoshTuplesCompleter({
            'index': link_completer,
        })

        super().__init__(rosh, completer)

    def handler(self, filters, cmd, *args):
        (pos, msg, kwargs) = self.parse_args(cmd, args)

        assert pos is None

        self.dump_addr(**kwargs)

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
                ifa_flags.lookup_str(addr['flags'])
            ])
        print(tbl)


is_rosh_command = True
rosh_command = RoshShowIpv6AddressCommand
