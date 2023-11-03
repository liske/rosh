from pyroute2 import netns

from rosh.commands import RoshCommand
from rosh.completer import netns_completer
from rosh.output import RoshOutputTable

class RoshShowNetnsCommand(RoshCommand):
    def __init__(self, rosh):
        super().__init__(rosh, netns_completer)

    def handler(self, cmd, *args):
        tbl = RoshOutputTable()
        tbl.field_names = ['NetNS']
        tbl.align = 'l'
        tbl.sortby = 'NetNS'
        tbl.add_rows([[x] for x in netns.listnetns()])
        print(tbl)


is_rosh_command = True
rosh_command = RoshShowNetnsCommand
