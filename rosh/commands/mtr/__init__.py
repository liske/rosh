import shutil

from rosh.commands import RoshSystemCommand


mtr_exe = shutil.which('mtr')

class RoshMtrCommand(RoshSystemCommand):
    description = 'run mtr command'

    def __init__(self, rosh):
        super().__init__(rosh, mtr_exe)

is_rosh_command = mtr_exe is not None
rosh_command = RoshMtrCommand
