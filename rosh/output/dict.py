import pprint
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import TerminalFormatter
import yaml

class RoshOutputDict():
    def print(self, obj):
        formated = yaml.dump(obj, sort_keys=True)
        print(highlight(formated, YamlLexer(), TerminalFormatter()), end="")
