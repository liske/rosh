# ChangeLog

## 0.1.6 - 2023-12-23

Changes:
- config: update default config filename to /etc/rosh.conf

## 0.1.5 - 2023-12-23

Changes:
- commands: add ifstatecli command
- doc: add commented default configuration

## 0.1.4 - 2023-12-18

Changes:
- commands: add ifalias output for show interface
- commands: move ethtool --identify into dedicated command
- config: add config file support
- prompt: allow command abbreviation
- prompt: set default completion style from COLUMN to READLINE_LIKE

## 0.1.3 - 2023-11-12

Changes:
- commands: make tables more compact
- commands: improve validation
- commands: add ethtool --reset and --negotiate commands

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
