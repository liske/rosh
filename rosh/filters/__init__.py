from abc import ABC, abstractmethod
from prompt_toolkit.completion import DummyCompleter


class RoshFilter(ABC):
    '''
    Base class for filters.
    '''

    min_args = 0
    max_args = None
    completer = DummyCompleter()

    @abstractmethod
    def __init__(self, rosh, cmd, *args):
        self.rosh = rosh

    @abstractmethod
    def match(self, obj):
        return self.match_item(obj)

    @classmethod
    def validate(cls, rosh, cmd, args):
        if len(args) < cls.min_args:
            return (len(args), "missing argument")

        if cls.max_args is not None and len(args) > cls.max_args:
            return (len(args), "too many arguments")

        if len(args) > 0:
            if callable(getattr(cls.completer, 'parse_value', None)):
                try:
                    cls.completer.parse_value(rosh, None, args[0])
                except ValueError as err:
                    return (1, str(err))

        return (None, None)

    @classmethod
    def filter_test_item(cls, filters, item):
        if filters is None:
            return True

        for flt in filters:
            if not flt.match(str(item)):
                return False

        return True

    @classmethod
    def filter_test_list(cls, filters, row):
        if filters is None:
            return True

        for flt in filters:
            if not flt.combine([flt.match(col) for col in row]):
                return False

        return True
