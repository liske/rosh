from socket import AF_INET

from rosh.commands.show.ipv6.rule import RoshShowIpv6RuleCommand


class RoshShowIpRuleCommand(RoshShowIpv6RuleCommand):
    def __init__(self, rosh):
        super().__init__(rosh)
        self.family = AF_INET


is_rosh_command = True
rosh_command = RoshShowIpRuleCommand
