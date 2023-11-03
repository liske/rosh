from rosh.commands import RoshCommand
from rosh.completer import link_completer
from rosh.output import RoshOutputTable

class RoshShowIpNeighbourCommand(RoshCommand):
    def __init__(self, rosh):
        super().__init__(rosh, link_completer)

    def handler(self, cmd, *args):
        if len(args) == 0:
            self.handler_brief()
        elif len(args) == 1:
            self.handler_iface(args[0])

    def dump_neigh(self, **filter):
        print(filter)
        tbl = RoshOutputTable()
        tbl.field_names = ['dst', 'lladdr', 'ifname', 'flags', 'state']
        tbl.align['dst'] = 'l'
        tbl.align['ifname'] = 'l'
        tbl.sortby = 'dst'

        for neigh in self.rosh.ipr.get_neighbours(**filter):
            tbl.add_row([
                neigh.get_attr('NDA_DST'),
                neigh.get_attr('NDA_LLADDR'),
                neigh['ifindex'],
                neigh['flags'],
                neigh['state']
            ])
        print(tbl)

    def handler_brief(self):
        self.dump_neigh()

    def handler_iface(self, ifname):
        self.dump_neigh(ifname=ifname)


is_rosh_command = True
rosh_command = RoshShowIpNeighbourCommand
