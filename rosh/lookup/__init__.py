import pyroute2.netlink.rtnl.ndmsg
import pyroute2.netlink.rtnl.ifaddrmsg

class LookupID():
    def __init__(self, entries):
        self.str2id = entries
        self.id2str = {v: k for k, v in self.str2id.items()}

    def lookup_id(self, key):
        if type(key) == int or key.isdecimal():
            return int(key)

        return self.str2id[key]

    def lookup_str(self, key):
        return self.id2str.get(key, key)

neigh_flags = LookupID(pyroute2.netlink.rtnl.ndmsg.flags)
neigh_states = LookupID(pyroute2.netlink.rtnl.ndmsg.states)

ifa_flags_map = {x[6:].lower(): y for x,y in pyroute2.netlink.rtnl.ifaddrmsg.IFA_F_NAMES.items()}
ifa_flags = LookupID(ifa_flags_map)
