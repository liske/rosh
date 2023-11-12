from prettytable import PrettyTable


class RoshOutputTable(PrettyTable):
    def __init__(self):
        super().__init__(
            header_style='upper',
            border=False,
            preserve_internal_border=True
        )
