from prompt_toolkit.validation import Validator, ValidationError
import shlex

class RoshValidator(Validator):
    def __init__(self, rosh):
        super().__init__()

        self.rosh = rosh

    def validate(self, document):
        text = shlex.split(document.text)

        # skip empty input
        if len(text) == 0:
            return

        (cmd, filters) = self.rosh.parse_filters(text)

        # skip when there is no command
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

        # check filters
        if filters:
            for filt in filters:
                # get filter class
                (flt, arg0, args) = self.rosh.get_filter(*filt)

                if not flt:
                    partial = shlex.join(text[:len(cmd) + 3])
                    raise ValidationError(
                        message='Unknown filter: {}'.format(arg0),
                        cursor_position=len(partial),
                    )

                # validate filter input
                (pos, message) = flt.validate(self.rosh, arg0, args)

                if pos is not None:
                    partial = shlex.join(text[:len(cmd) + pos + 3])
                    cursor = len(partial)

                    raise ValidationError(
                        message=message,
                        cursor_position=cursor,
                    )
