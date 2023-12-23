from prompt_toolkit.completion import WordCompleter
import shutil

from rosh.commands import RoshSystemCommand


ifstatecli_exe = shutil.which('ifstatecli')

class RoshIfstateCommand(RoshSystemCommand):
    description = 'run ifstatecli command'

    def __init__(self, rosh):
        completer = WordCompleter([
            'apply',
            'check',
            'shell',
            'show',
            'showall'
        ])
        super().__init__(rosh, ifstatecli_exe, completer)
        rosh.config['command.ifstatecli'] = {
            'config_file': '',
            'quiet': False,
            'soft_schema': False,
            'verbose': False
        }

    def handler(self, cmd, *args):
        config_args = []

        config_file = self.rosh.config['command.ifstatecli'].get('config_file')
        if config_file:
            config_args.append('-c')
            config_args.append(config_file)

        if self.rosh.config['command.ifstatecli'].getboolean('quiet'):
            config_args.append('-q')

        if self.rosh.config['command.ifstatecli'].getboolean('soft_schema'):
            config_args.append('-s')

        if self.rosh.config['command.ifstatecli'].getboolean('verbose'):
            config_args.append('-v')

        super().handler(cmd, *config_args, *args)


is_rosh_command = ifstatecli_exe is not None
rosh_command = RoshIfstateCommand
