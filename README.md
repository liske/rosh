# RoSh - Router Shell

## About

This is an interactive diagnostic shell for Linux-based routers. It is inspired by the CLI of classic network devices (e.g. Cisco IOS) and implements diagnostic functions similar to iproute2/bridge/ethtool/tc/wireguard. It is explicitly not intended for configuration changes, but to support the analysis of software routers by network engineers.

![RoSh demo](doc/demo.gif)


## Commands

The following commands are available:

```
disable
  interface        disable (shutdown) an interface
    {ifname}
enable
  interface        enable (no shutdown) an interface
    {ifname}
exit               exit from rosh
help               show command help
identify
  interface        initiate the adapter identify by sight procedure
    {ifname}
ifstatecli         run ifstatecli command
  <apply|check|shell|show|showall>
lbu                run lbu command
  <commit|ci|diff|exclude|include|list|ls|list-backup|lb|package|pkg|revert|status|st>
monitor         monitor for changes
  <all|none|address|interface|neigh|netconf|prefix|route|rule> {ifname}
mtr                run mtr command
netns              change active netns namespace for subsequent commands
  {netns}
ping               run ping command
renegotiate
  interface        restart auto-negotiate on an interface
    {ifname}
reset
  interface        reset an interface
    {ifname} <flags|mgmt|irq|dma|filter|offload|mac|phy|ram|dedicated|all>
shell              launch a interactive system shell
show
  bridge
    fdb            show bridge forwarding database
      [dst <{ipv6}>] [ifindex <{ifname}>] [state <{state}>]
  interface        show interface details
    {ifname} [channels|coalesce|driver|eee|features|module|pause|priv-flags|ring|settings|stats|tstamp|tunnels]
  ip
    address        show assigned ipv4 addresses
      [index <{ifname}>]
    neighbour      show ipv4 neighbour cache entries (ARP)
      [dst <{ip}>] [ifindex <{ifname}>] [state <{state}>]
    route          show ipv4 routes
      [dst <{pfx}>] [gateway <{ip}>] [oif <{ifname}>] [proto <{proto}>] [scope <{scope}>] [table <{table}>]
    rule           show ipv4 routing policy rules
      [dst <{pfx}>] [iif <{ifname}>] [oif <{ifname}>] [proto <{proto}>] [src <{pfx}>] [table <{table}>]
  ipv6
    address        show assigned ipv6 addresses
      [index <{ifname}>]
    neighbour      show ipv4 neighbour cache entries
      [dst <{ipv6}>] [ifindex <{ifname}>] [state <{state}>]
    route          show ipv6 routes
      [dst <{pfxv6}>] [gateway <{ipv6}>] [oif <{ifname}>] [proto <{proto}>] [scope <{scope}>] [table <{table}>]
    rule           show ipv6 routing policy rules
      [dst <{pfxv6}>] [iif <{ifname}>] [oif <{ifname}>] [proto <{proto}>] [src <{pfxv6}>] [table <{table}>]
  netns            show netns namespaces
    {netns}
ssh                run ssh command
tcpdump            run tcpdump command
telnet             run telnet command
traceroute         run traceroute command
```

## Install

### Alpine Linux

RoSh is available in the community repository of [Alpine Linux edge](https://pkgs.alpinelinux.org/packages?name=rosh).

### PyPi

RoSh is available at [PyPi](https://pypi.org/project/rosh/) and can be installed via `pip`:

```
$ pip install rosh
```
