from socket import AF_INET

from rosh.commands.show.ipv6.address import RoshShowIpv6AddressCommand


class RoshShowIpAddressCommand(RoshShowIpv6AddressCommand):
    def __init__(self, rosh):
        super().__init__(rosh)
        self.family = AF_INET


is_rosh_command = True
rosh_command = RoshShowIpAddressCommand
