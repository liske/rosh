from prompt_toolkit.completion import WordCompleter
import shutil

from rosh.commands import RoshCommand, RoshSystemCommand
from rosh.completer import link_completer, RoshPeerCompleter
from rosh.output import RoshOutputTable


ethtool_exe = shutil.which('ethtool')

class RoshEthtoolCommand(RoshSystemCommand):
    def __init__(self, rosh):
        super().__init__(rosh, ethtool_exe)

class RoshShowInterfaceCommand(RoshCommand):
    description = 'show interface details'

    def __init__(self, rosh):
        self.ethtool_args = {
            'settings': '-I',
            'coalesce': '-c',
            'driver': '-i',
            'eee': '--show-eee',
            'features': '-k',
            'module': '-m',
            'pause': '-a',
            'ring': '-g',
            'stats': '-S',
            'tstamp': '-T',
        }
        self.ethtool_command = RoshEthtoolCommand(rosh)

        if ethtool_exe is None:
            completer = link_completer
        else:
            completer = RoshPeerCompleter(link_completer, WordCompleter(['', *self.ethtool_args.keys()]))

        super().__init__(rosh, completer)

    def handler(self, cmd, *args):
        if len(args) == 0:
            self.handler_brief()
        elif len(args) == 1:
            self.handler_iface(args[0])
        elif len(args) == 2:
            self.handler_ethtool(args[0], args[1])

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
            self.print_link_details(link)


    def print_link_details(self, link):
        self.output.print_header('States')
        self.print_link_states(link)

        print()
        self.output.print_header('Addresses')
        self.print_link_addresses(link)

        if link.get_attr('IFLA_MTU') is not None:
            print()
            self.output.print_header('MTU')
            self.print_link_mtu(link)

        print()
        self.output.print_header('Link')
        self.print_link_device(link)

    def print_link_states(self, link):
        details = {
            'admin': self.output.quote_value(link['state']),
        }

        oper = link.get_attr('IFLA_OPERSTATE').lower()
        if oper == 'unknown':
            details['oper'] = self.output.quote_na('unknown')
        elif oper != link['state']:
            details['oper'] = self.output.quote_warn(oper)
        else:
            details['oper'] = self.output.quote_ok(oper)

        if link['state'] == 'up':
            details['carrier'] = self.output.quote_ok('up') if link.get_attr('IFLA_CARRIER') else self.output.quote_warn('down')
        else:
            details['carrier'] = self.output.quote_att('up') if link.get_attr('IFLA_CARRIER') else self.output.quote_ok('down')

        details['promisc'] = self.output.quote_att('yes') if link.get_attr('IFLA_PROMISCUITY') else 'no'

        self.output.print_dict(details)

    def print_link_mtu(self, link):
        mtu = {
            'set': self.output.quote_value(link.get_attr('IFLA_MTU')),
        }
        for limit in ['min', 'max']:
            val = link.get_attr(f'IFLA_{limit.upper()}_MTU', 0)
            if val > 0:
                mtu[limit] = val

        self.output.print_dict(mtu)

    def print_link_addresses(self, link):
        addresses = {
            'L2': {
                'effective': self.output.quote_value(link.get_attr('IFLA_ADDRESS'))
            },
        }

        if link.get_attr('IFLA_PERM_ADDRESS') is not None:
            addresses['L2']['permanent'] = link.get_attr('IFLA_PERM_ADDRESS')

        ipaddrs = []
        for addr in self.rosh.ipr.get_addr(index=link['index']):
            ipaddrs.append(self.output.quote_value(addr.get_attr('IFA_ADDRESS') +
                              '/' + str(addr['prefixlen'])))
        if ipaddrs:
            addresses['L3'] = ipaddrs

        self.output.print_dicts(addresses)

    def print_link_device(self, link):
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

        self.output.print_dict(device)

    def handler_ethtool(self, iface, cmd):
        self.ethtool_command.handler(None, self.ethtool_args[cmd], iface)

    def validate(self, cmd, args):
        if len(args) > 2:
            return (2, "to many parameters (>2)")

        if len(args) >= 1 and not args[0] in link_completer.get_links():
            return (0, f"{args[0]} does not exist")

        if len(args) == 2 and not args[1] in self.ethtool_args:
            return (1, f"subcommand {args[1]} is invalid")

        return (None, None)

is_rosh_command = True
rosh_command = RoshShowInterfaceCommand
