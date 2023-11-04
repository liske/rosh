from pyroute2 import netns

from rosh.commands import RoshCommand
from rosh.completer import netns_completer
from rosh.output import RoshOutputTable

class RoshShowNetnsCommand(RoshCommand):
    description = 'show netns namespaces'

    def __init__(self, rosh):
        super().__init__(rosh, netns_completer)

    def handler(self, cmd, *args):
        tbl = RoshOutputTable()
        tbl.field_names = ['NetNS']
        tbl.align = 'l'
        tbl.sortby = 'NetNS'
        tbl.add_rows([[x] for x in netns.listnetns()])
        print(tbl)


    def validate(self, cmd, args):
        if len(args) > 1:
            return (1, "to many parameters (>1)")

        if len(args) == 1 and not args[0] in netns.listnetns():
            return (0, f"{args[0]} does not exist")

        return (None, None)

is_rosh_command = True
rosh_command = RoshShowNetnsCommand
