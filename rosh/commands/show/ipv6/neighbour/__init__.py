from socket import AF_INET6

from rosh.commands import RoshTuplesCommand
from rosh.completer import link_completer, proto_completer, neighstate_completer, RoshIpCompleter, RoshTuplesCompleter
from rosh.filters import RoshFilter
from rosh.lookup import neigh_flags, neigh_states
from rosh.output import RoshOutputTable

class RoshShowIpv6NeighbourCommand(RoshTuplesCommand):
    description = 'show ipv4 neighbour cache entries'

    def __init__(self, rosh, family=AF_INET6):
        self.family = family

        completer = RoshTuplesCompleter({
            'dst': RoshIpCompleter(family),
            'ifindex': link_completer,
            'state': neighstate_completer,
        })

        super().__init__(rosh, completer)

    def handler(self, filters, cmd, *args):
        (pos, msg, kwargs) = self.parse_args(cmd, args)

        assert pos is None

        self.dump_neigh(filters, **kwargs)

    def dump_neigh(self, prompt_filters, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['dst', 'lladdr', 'ifname', 'flags', 'state']
        tbl.align['dst'] = 'l'
        tbl.align['ifname'] = 'l'
        tbl.sortby = 'dst'

        for neigh in self.rosh.ipr.get_neighbours(family=self.family, **filter):
            row = [
                neigh.get_attr('NDA_DST',''),
                neigh.get_attr('NDA_LLADDR', '(incomplete)'),
                self.rosh.idx_to_ifname(neigh['ifindex']),
                neigh_flags.lookup_str(neigh['flags']) or '-',
                neigh_states.lookup_str(neigh['state']) or '-'
            ]

            if RoshFilter.filter_test_list(prompt_filters, row):
                tbl.add_row(row)
        print(tbl)


is_rosh_command = True
rosh_command = RoshShowIpv6NeighbourCommand
