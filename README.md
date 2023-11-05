# RoSh - Router Shell

**WARNING** *This project is still in an early stage of development, and most of its intended function is missing!*

This is a interactive diagnostic shell for (software|linux)-based routers. It's inspired by the CLI of network equipment (i.e. Cisco IOS) and implements simular diagnostic commands like the iproute2/bridge/ethtool/tc/wireguard commands.

![rosh demo](doc/demo.gif)


## Commands

The following commands are available:

```
- exit               exit from rosh
- netns              change active netns namespace for subsequent commands
    {netns}
- ping               execute ping command
- shell              launch a interactive system shell
- show
  - interface        show interface details
      {ifname} [|settings|coalesce|driver|eee|features|module|pause|ring|stats|tstamp]
  - ip
    - address        show assigned ipv4 addresses
        {ifname}
    - neighbour      show ipv4 neighbour cache entries (ARP)
        [dev <{ifname}>] [proto <{proto}>]
    - route          show ipv4 routes
    - rule           show ipv4 routing policy rules
        {ifname}
  - ipv6
    - address        show assigned ipv6 addresses
        {ifname}
    - neighbour      show ipv4 neighbour cache entries
        [dev <{ifname}>] [proto <{proto}>]
    - route          show ipv6 routes
    - rule           show ipv6 routing policy rules
        {ifname}
  - netns            show netns namespaces
      {netns}
- ssh                execute ssh command
- tcpdump            execute tcpdump command
- telnet             execute telnet command
- traceroute         execute traceroute command
```

## Install

RoSh is available at [PyPi](https://pypi.org/project/rosh/) and can be installed via `pip`:

```
$ pip install rosh
```
