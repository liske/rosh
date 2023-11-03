from glob import glob
import os
import re

class RTLookup():
    def __init__(self, name):
        self.name = name
        self.str2id = {}
        self.id2str = {}

        try:
            fn = os.path.join('/etc/iproute2', name)
            with open(fn, 'r') as fp:
                self._parse(fp)

            for fn in glob(os.path.join('/etc/iproute2', "{}.d".format(name), "*.conf")):
                with open(fn, 'r') as fp:
                    self._parse(fp)
        except OSError:
            pass

    def _parse(self, fp):
        for line in fp:
            m = re.search(r'^(\d+)\s+(\S+)$', line)
            if m:
                self.str2id[m.group(2)] = int(m.group(1))
                self.id2str[int(m.group(1))] = m.group(2)

    def lookup_id(self, key):
        if type(key) == int or key.isdecimal():
            return int(key)

        return self.str2id[key]

    def lookup_str(self, key):
        return self.id2str.get(key, key)


tables = RTLookup('rt_tables')
realms = RTLookup('rt_realms')
scopes = RTLookup('rt_scopes')
protos = RTLookup('rt_protos')
group = RTLookup('group')
