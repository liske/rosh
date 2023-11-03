from prompt_toolkit.completion import WordCompleter
from pyroute2 import netns, IPRoute
from shlex import quote

class RoshLinkCompleter(WordCompleter):
    def __init__(self):
        self.ipr = None
        super().__init__(self.get_links)

    def set_ipr(self, ipr):
        self.ipr = ipr

    def get_links(self):
        links = []
        if self.ipr is not None:
            for link in self.ipr.get_links():
                links.append(quote(link.get_attr('IFLA_IFNAME')))
        return links

class RoshNetNSCompleter(WordCompleter):
    def __init__(self):
        super().__init__(self.get_netns)

    def get_netns(self):
        l = []
        for ns in netns.listnetns():
            l.append(quote(ns))
        return l

link_completer = RoshLinkCompleter()
netns_completer = RoshNetNSCompleter()
