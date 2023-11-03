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
            partial = shlex.join(cmd[:depth-1])
            cursor = len(partial)

            if depth > len(cmd):
                raise ValidationError(
                    message='command incomplete',
                    cursor_position=cursor,
                )
            else:
                if cursor > 0:
                    cursor += 1
                partial += ' '
                partial += shlex.quote(cmd[depth-1])

                raise ValidationError(
                    message='Unknown command: {}'.format(partial),
                    cursor_position=cursor,
                )

        # check command param
        (pos, message) = command.validate(arg0, args)
        if pos is not None:
            partial = shlex.join(cmd[:depth + pos])
            cursor = len(partial)
            if cursor > 0:
                cursor += 1

            raise ValidationError(
                message=message,
                cursor_position=cursor,
            )
