# ChangeLog

## 0.1.2 - 2023-11-11

Changes:
- commands: add more ethtool details (channels, identify, priv-flags, tunnels)
- commands: add mtr command
- commands: add validation for simple commands
- commands: add disable and enable command for interfaces
- prompt: dump netns list on startup (if any)

## 0.1.1 - 2023-11-11

Changes:
- commands: add lbu command
- commands: set PS1 for shell command
- prompt: add banner and update styling

Fixes:
- commands: fix exception if ethtool is missing

## 0.1.0 - 2023-11-06

Changes:
- commands: add help command
- commands: add show bridge fdb command
- commands: improve command list layout 
- completers: sort word lists

Fixes:
- commands: fix pushns regression for external commands

## 0.0.2 - 2023-11-05

Changes:
- cli: add initial parsing of parameters
- commands: refactor pyroute2.get_* commands and make filters work
- commands: use basename for `argv[0]` on external commands
- completers: add completion for various tables (`/etc/iproute2/`)
- completers: add completion for various states & flags (addr, pfx, neigh)
- prompt: add fancy styling

Fixes:
- traceroute: fix command name

## 0.0.1 - 2023-11-04

Initial release.
