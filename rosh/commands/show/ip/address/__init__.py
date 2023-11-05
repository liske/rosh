from socket import AF_INET

from rosh.commands.show.ipv6.address import RoshShowIpv6AddressCommand


class RoshShowIpAddressCommand(RoshShowIpv6AddressCommand):
    description = 'show assigned ipv4 addresses'

    def __init__(self, rosh):
        super().__init__(rosh, AF_INET)


is_rosh_command = True
rosh_command = RoshShowIpAddressCommand
