from rosh.filters import RoshFilter

import re

class RoshIncludeFilter(RoshFilter):
    description = 'include items matching a regex'

    min_args = 1
    max_args = 1
    combine = any

    def __init__(self, rosh, cmd, *args):
        self.regex = re.compile(args[0])

    def match(self, item):
        return self.regex.search(str(item)) is not None

is_rosh_filter = True
rosh_filter = RoshIncludeFilter
