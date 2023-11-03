from socket import AF_INET6

from rosh.commands import RoshCommand
from rosh.completer import link_completer
from rosh.output import RoshOutputTable

class RoshShowIpv6NeighbourCommand(RoshCommand):
    def __init__(self, rosh):
        super().__init__(rosh, link_completer)
        self.family = AF_INET6

    def handler(self, cmd, *args):
        if len(args) == 0:
            self.handler_brief()
        elif len(args) == 1:
            self.handler_iface(args[0])

    def dump_neigh(self, **filter):
        tbl = RoshOutputTable()
        tbl.field_names = ['dst', 'lladdr', 'ifname', 'flags', 'state']
        tbl.align['dst'] = 'l'
        tbl.align['ifname'] = 'l'
        tbl.sortby = 'dst'

        for neigh in self.rosh.ipr.get_neighbours(family=self.family, **filter):
            tbl.add_row([
                neigh.get_attr('NDA_DST'),
                neigh.get_attr('NDA_LLADDR'),
                self.rosh.idx_to_ifname(neigh['ifindex']),
                neigh['flags'],
                neigh['state']
            ])
        print(tbl)

    def handler_brief(self):
        self.dump_neigh()

    def handler_iface(self, ifname):
        self.dump_neigh(ifname=ifname)

    def validate(self, cmd, args):
        if len(args) > 1:
            return (1, "to many parameters (>1)")

        if len(args) == 1 and not args[0] in link_completer.get_links():
            return (0, f"{args[0]} does not exist")

        return (None, None)


is_rosh_command = True
rosh_command = RoshShowIpv6NeighbourCommand
