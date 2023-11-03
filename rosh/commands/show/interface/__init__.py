from pyroute2 import netns

from rosh.commands import RoshCommand
from rosh.completer import link_completer
from rosh.output import RoshOutputTable

class RoshShowInterfaceCommand(RoshCommand):
    def __init__(self, rosh):
        super().__init__(rosh, link_completer)

    def handler(self, cmd, *args):
        if len(args) == 1:
            self.handler_brief()
        elif len(args) == 2:
            self.handler_iface(args[1])

    def handler_brief(self):
        tbl = RoshOutputTable()
        tbl.field_names = ['idx', 'ifname', 'kind', 'admin', 'oper', 'carrier']
        tbl.align['idx'] = 'r'
        tbl.align['ifname'] = 'l'
        tbl.sortby = 'ifname'

        for link in self.rosh.ipr.get_links():
            ifname = link.get_attr('IFLA_IFNAME')
            kind = link.get_attr('IFLA_PARENT_DEV_BUS_NAME', '-')
            link_info = link.get_attr('IFLA_LINKINFO')

            if link_info is not None:
                kind = link_info.get_attr('IFLA_INFO_KIND')


            tbl.add_row([
                link['index'],
                ifname,
                kind,
                link['state'],
                link.get_attr('IFLA_OPERSTATE').lower(),
                'up' if link.get_attr('IFLA_CARRIER') else 'down',
            ])
        print(tbl)

    def handler_iface(self, ifname):
        for link in self.rosh.ipr.get_links(ifname=ifname):
            output = {
                ifname: self.get_link_details(link)
            }


    def get_link_details(self, link):
        self.print({
            'States': self.get_link_states(link)
        })

        print()
        self.print({
            'Addresses': self.get_link_addresses(link)
        })

        if link.get_attr('IFLA_MTU') is not None:
            print()
            self.print({
                'MTU': self.get_link_mtu(link)
            })

        print()
        self.print({
            'Link': self.get_link_device(link)
        })

    def get_link_states(self, link):
        return {
            'admin': link['state'],
            'oper': link.get_attr('IFLA_OPERSTATE').lower(),
            'carrier': 'up' if link.get_attr('IFLA_CARRIER') else 'down',
            'promisc': 'yes' if link.get_attr('IFLA_PROMISCUITY') else 'no',
        }

    def get_link_mtu(self, link):
        mtu = {
            'current': link.get_attr('IFLA_MTU'),
        }
        for limit in ['min', 'max']:
            val = link.get_attr(f'IFLA_{limit.upper()}_MTU', 0)
            if val > 0:
                mtu[limit] = val

        return mtu

    def get_link_addresses(self, link):
        addresses = {
            'L2': {
                'current': link.get_attr('IFLA_ADDRESS')
            },
        }

        if link.get_attr('IFLA_PERM_ADDRESS') is not None:
            addresses['L2']['permanent'] = link.get_attr('IFLA_PERM_ADDRESS')

        ipaddrs = []
        for addr in self.rosh.ipr.get_addr(index=link['index']):
            ipaddrs.append(addr.get_attr('IFA_ADDRESS') +
                              '/' + str(addr['prefixlen']))
        if ipaddrs:
            addresses['L3'] = ipaddrs

        return addresses                

    def get_link_device(self, link):
        device = {
            'index': link['index'],
        }

        link_info = link.get_attr('IFLA_LINKINFO')

        if link_info is not None:
            device['kind'] = link_info.get_attr('IFLA_INFO_KIND')

        bus = link.get_attr('IFLA_PARENT_DEV_BUS_NAME')
        if bus:
            device['bus'] = bus

        dev = link.get_attr('IFLA_PARENT_DEV_NAME')
        if dev:
            device['device'] = dev

        return device


is_rosh_command = True
rosh_command = RoshShowInterfaceCommand
