from prompt_toolkit.completion import Completer, WordCompleter
from prompt_toolkit.document import Document
from pyroute2 import netns, IPRoute
import shlex

from rosh.commands import RoshCommand


class RoshPeerCompleter(Completer):
    def __init__(self, base_completer, sub_completer):
        self.base_completer = base_completer
        self.sub_completer = sub_completer

    def get_completions(self, document, complete_event):
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # if there is a space and use the subcompleter.
        if " " in text:
            first_term = text.split()[0]
            remaining_text = text[len(first_term) :].lstrip()
            move_cursor = len(text) - len(remaining_text) + stripped_len

            new_document = Document(
                remaining_text,
                cursor_position=document.cursor_position - move_cursor,
            )

            yield from self.sub_completer.get_completions(new_document, complete_event)

        # no space in the input: use the base completer
        else:
            yield from self.base_completer.get_completions(document, complete_event)

class RoshTuplesCompleter(Completer):
    def __init__(self, tuples):
        self.tuples = {}

        # build recursive completer
        for keyword, completer in tuples.items():
            self.tuples[keyword] = RoshPeerCompleter(completer, self)

        # keyword completer
        self.keywords_completer = WordCompleter(tuples.keys())

    def get_completions(self, document, complete_event):
        # Split document.
        text = document.text_before_cursor.lstrip()
        stripped_len = len(document.text_before_cursor) - len(text)

        # if there is a space and use a subcompleter, if available
        if " " in text:
            first_term = text.split()[0]
            if first_term in self.tuples:
                remaining_text = text[len(first_term) :].lstrip()
                move_cursor = len(text) - len(remaining_text) + stripped_len

                new_document = Document(
                    remaining_text,
                    cursor_position=document.cursor_position - move_cursor,
                )

                yield from self.tuples[first_term].get_completions(new_document, complete_event)
            else:
                return []
        # no space in the input: use the base completer
        else:
            yield from self.keywords_completer.get_completions(document, complete_event)

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
                links.append(shlex.quote(link.get_attr('IFLA_IFNAME')))
        return links

class RoshNetNSCompleter(WordCompleter):
    def __init__(self):
        super().__init__(self.get_netns)

    def get_netns(self):
        l = []
        for ns in netns.listnetns():
            l.append(shlex.quote(ns))
        return l

link_completer = RoshLinkCompleter()
netns_completer = RoshNetNSCompleter()
