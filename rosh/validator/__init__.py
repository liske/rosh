from prompt_toolkit.validation import Validator, ValidationError
import shlex

class RoshValidator(Validator):
    def __init__(self, rosh):
        super().__init__()

        self.rosh = rosh

    def validate(self, document):
        cmd = shlex.split(document.text)

        # skip empty input
        if len(cmd) == 0:
            return

        (depth, command, arg0, args) = self.rosh.get_command(*cmd)

        # no command found
        if not command:
            if depth > len(cmd):
                raise ValidationError(
                    message='command incomplete',
                    cursor_position=len(document.text),
                )
            else:
                partial = shlex.join(cmd[:depth])
                cursor = len(partial)

                raise ValidationError(
                    message='Unknown command: {}'.format(partial),
                    cursor_position=cursor,
                )

        # check command param
        (pos, message) = command.validate(arg0, args)
        if pos is not None:
            partial = shlex.join(cmd[:depth + pos + 1])
            cursor = len(partial)

            raise ValidationError(
                message=message,
                cursor_position=cursor,
            )
