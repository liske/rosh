from prompt_toolkit import print_formatted_text as print
from prompt_toolkit.completion import WordCompleter
import shutil

from rosh.commands import RoshCommand
from rosh.commands.ifstatecli import ifstatecli_exe

try:
    import pygments
    from pygments.lexers import YamlLexer
    from prompt_toolkit.formatted_text import PygmentsTokens

    # pygements imported successfully
    has_pygements = 1
except ImportError:
    # no pygements available
    has_pygements = 0


class RoshShowIfstateConfigCommand(RoshCommand):
    description = "show ifstate's config file"

    def handler(self, filters, cmd, *args):
        config_args = []

        config_file = self.rosh.config['command.ifstatecli'].get('config_file')

        if not config_file:
            config_file = '/etc/ifstate/config.yml'

        try:
            with open(config_file) as fh:
                code = fh.read().encode('utf8')
        except IOError as ex:
            print(f'could not read file: {ex}')
            return
        except UnicodeEncodeError as ex:
            print(f'encoding problem: {ex}')
            return

        if has_pygements:
            tokens = list(pygments.lex(code, lexer=YamlLexer()))
            print(PygmentsTokens(tokens))
        else:
            print(code)

    def validate(self, cmd, args):
        if len(args) > 0:
            return (0, "no parameters allowed")

        return (None, None)


is_rosh_command = ifstatecli_exe is not None
rosh_command = RoshShowIfstateConfigCommand
