from prompt_toolkit import print_formatted_text as print
import shutil
import signal
import subprocess
from threading import Thread

from rosh.commands import RoshCommand
from rosh.completer import link_completer, RoshPeerCompleter, RoshWordCompleter
from rosh.filters import RoshFilter

ip_exe = shutil.which('ip')

MONITOR_COMMANDS = [
                'all',
                'none',
                'address',
                'interface',
                'neigh',
                'netconf',
                'prefix',
                'route',
                'rule',
]

class RoshMonitor(RoshCommand):
    description = 'monitor for network changes'

    def __init__(self, rosh):
        self.monitor_process = None
        self.monitor_thread = None

        rosh.register_quit_fn(self.reset_monitor)

        completer = RoshPeerCompleter(
            RoshWordCompleter(MONITOR_COMMANDS),
            link_completer
        )
        super().__init__(rosh, completer, min_args=1)

    def handler(self, filters, cmd, *args):
        if args[0] == 'none':
            self.reset_monitor()
        else:
            self.reset_monitor()

            # use iproute2 naming
            if args[0] == 'interface':
                args[0] = 'link'

            # always enable label prefix
            args = list(args)
            args.insert(1, 'label')

            # add 'dev' prefix to interface name, if any
            if len(args) > 2:
                args.insert(2, 'dev')

            self.start_monitor(filters, *args)

    def validate(self, cmd, args):
        result = super().validate(cmd, args)
        if result[0] != None:
            return result
        

        if len(args) > 2:
            return (2, "to many parameters (>2)")

        if not args[0] in MONITOR_COMMANDS:
            return (0, f"{args[0]} is no valid monitor object")

        if len(args) > 1 and not args[1] in link_completer.get_links():
            return (1, f"interface {args[1]} does not exist")

        return (None, None)

    def reset_monitor(self):
        # kill `ip monitor` process
        if self.monitor_process is not None:
            self.monitor_process.kill()
            self.monitor_process = None

        # terminate process
        if self.monitor_thread is not None:
            self.monitor_thread.join()
            self.monitor_thread = None

    def start_monitor(self, *args):
        self.monitor_thread = Thread(target=self.monitor_worker, name='RoshMonitor', args=args)
        self.monitor_thread.start()

    def monitor_worker(self, filters, *args):
        def preexec_cb():
            # Ignore the SIGINT signal by setting the handler to the standard
            # signal handler SIG_IGN.
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.monitor_process = subprocess.Popen(['ip', '-ts', 'monitor', *args],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           preexec_fn=preexec_cb)

        while True:
            line = self.monitor_process.stdout.readline().strip()

            if not line:
                self.monitor_process = None
                break

            line = line.decode(errors="ignore")

            if RoshFilter.filter_test_item(filters, line):
                print(line)


is_rosh_command = ip_exe is not None
rosh_command = RoshMonitor
