from ipaddress import ip_address, ip_network
from socket import AF_INET6

from rosh.commands import RoshTuplesCommand
from rosh.completer import link_completer, proto_completer, table_completer, RoshTuplesCompleter, RoshPfxCompleter
from rosh.filters import RoshFilter
from rosh.output import RoshOutputTable
from rosh.rtlookup import protos, tables


FRA_ACTIONS = {
     0: 'unspec',
     1: 'lookup',
     2: 'goto',
     3: 'nop',
     6: 'blackhole',
     7: 'unreach',
     8: 'prohibit',
}

class RoshShowIpv6RuleCommand(RoshTuplesCommand):
    description = 'show ipv6 routing policy rules'

    def __init__(self, rosh, family=AF_INET6):
        self.family = family

        completer = RoshTuplesCompleter({
            'dst': RoshPfxCompleter(family),
            'src': RoshPfxCompleter(family),
            'iif': link_completer,
            'oif': link_completer,
            'proto': proto_completer,
            'table': table_completer
        })

        super().__init__(rosh, completer)

    def handler(self, filters, cmd, *args):
        (pos, msg, kwargs) = self.parse_args(cmd, args)

        assert pos is None

        self.dump_rule(filters, **kwargs)

    def dump_rule(self, prompt_filters, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['prio', 'from', 'to', 'iif', 'oif', 'fwmark', 'ip_proto', 'action', 'target', 'proto']
        tbl.align['from'] = 'l'
        tbl.sortby = 'prio'

        for rule in self.rosh.ipr.get_rules(family=self.family, **filter):
            action = FRA_ACTIONS.get(rule['action'], rule['action'])
            if action == 'lookup':
                target = tables.lookup_str(rule.get_attr('FRA_TABLE', '-'))
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

            row = [
                rule.get_attr('FRA_PRIORITY', 0),
                dst,
                src,
                rule.get_attr('FRA_IIFNAME', '-'),
                rule.get_attr('FRA_OIFNAME', '-'),
                rule.get_attr('FRA_FWMARK', '-'),
                rule.get_attr('FRA_IP_PROTO', '-'),
                action,
                target,
                protos.lookup_str(rule.get('protocol', '-'))
            ]

            if RoshFilter.filter_test_list(prompt_filters, row):
                tbl.add_row(row)
        print(tbl)


is_rosh_command = True
rosh_command = RoshShowIpv6RuleCommand
