from socket import AF_INET

from rosh.commands.show.ipv6.route import RoshShowIpv6RouteCommand


class RoshShowIpRouteCommand(RoshShowIpv6RouteCommand):
    description = 'show ipv4 routes'

    def __init__(self, rosh):
        super().__init__(rosh)
        self.family = AF_INET


is_rosh_command = True
rosh_command = RoshShowIpRouteCommand
