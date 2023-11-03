from ipaddress import ip_address, ip_network
from socket import AF_INET6

from rosh.commands import RoshCommand
from rosh.completer import link_completer
from rosh.output import RoshOutputTable


FRA_ACTIONS = {
     0: 'unspec',
     1: 'lookup',
     2: 'goto',
     3: 'nop',
     6: 'blackhole',
     7: 'unreach',
     8: 'prohibit',
}

class RoshShowIpv6RuleCommand(RoshCommand):
    def __init__(self, rosh):
        super().__init__(rosh, link_completer)
        self.family = AF_INET6

    def handler(self, cmd, *args):
        if len(args) == 0:
            self.handler_brief()
        elif len(args) == 1:
            self.handler_iface(args[0])

    def dump_rule(self, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['prio', 'from', 'to', 'iif', 'oif', 'fwmark', 'ip_proto', 'action', 'target', 'proto']
        tbl.align['from'] = 'l'
        tbl.sortby = 'prio'

        for rule in self.rosh.ipr.get_rules(family=self.family, **filter):
            action = FRA_ACTIONS.get(rule['action'], rule['action'])
            if action == 'lookup':
                target = rule.get_attr('FRA_TABLE', '-')
            elif action == 'goto':
                target = rule.get_attr('FRA_GOTO', '-')
            else:
                target = '-'

            if 'dst_len' in rule and rule['dst_len'] > 0:
                dst = ip_network(
                    '{}/{}'.format(rule['dst'], rule['dst_len'])).with_prefixlen
            else:
                dst = 'all'

            if 'src_len' in rule and rule['src_len'] > 0:
                src = ip_network(
                    '{}/{}'.format(rule['src'], rule['src_len'])).with_prefixlen
            else:
                src = 'all'

            from pprint import pprint
            pprint(rule)
            tbl.add_row([
                rule.get_attr('FRA_PRIORITY', 0),
                dst,
                src,
                rule.get_attr('FRA_IIFNAME', '-'),
                rule.get_attr('FRA_OIFNAME', '-'),
                rule.get_attr('FRA_FWMARK', '-'),
                rule.get_attr('FRA_IP_PROTO', '-'),
                action,
                target,
                rule.get('protocol', '-')
            ])
        print(tbl)

    def handler_brief(self):
        self.dump_rule()

    def handler_iface(self, ifname):
        self.dump_rule(ifname=ifname)

    def validate(self, cmd, args):
        if len(args) > 1:
            return (1, "to many parameters (>1)")

        if len(args) == 1 and not args[0] in link_completer.get_links():
            return (0, f"{args[0]} does not exist")

        return (None, None)


is_rosh_command = True
rosh_command = RoshShowIpv6RuleCommand
