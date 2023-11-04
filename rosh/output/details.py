from prompt_toolkit import print_formatted_text as print, HTML

class RoshOutputDetails():
    def quote(self, text):
        return text

    def quote_na(self, text):
        return f'<grey>{text}</grey>'

    def quote_ok(self, text):
        return f'<green>{text}</green>'

    def quote_warn(self, text):
        return f'<red>{text}</red>'

    def quote_att(self, text):
        return f'<orange>{text}</orange>'

    def quote_value(self, text):
        return f'<aqua>{text}</aqua>'

    def print_header(self, hdr, indent=''):
        if indent == '':
            print(HTML(f'<u>{hdr}</u>'))
        else:
            print(f'{indent}{k}')

    def print_dict(self, dct, indent='  '):
        justify = max(len(str(v)) for v in dct.keys())

        for k, v in dct.items():
            print(f"{indent}{k.ljust(justify)}: ", end='')
            print(HTML(f'<b>{v}</b>'))

    def print_dicts(self, dcts, indent='  '):
        justify = 0
        for dct in dcts.values():
            if isinstance(dct, dict):
                justify = max(justify, *[len(str(v)) for v in dct.keys()])

        for hdr, dct in dcts.items():
            print(f'{indent}{hdr}')

            if isinstance(dct, dict):
                for k, v in dct.items():
                    print(f"{indent}  {k.ljust(justify)}: ", end='')
                    print(HTML(f'<b>{v}</b>'))
            elif isinstance(dct, list):
                for v in dct:
                    print(HTML(f'{indent}  - <b>{v}</b>'))
            else:
                print(HTML(f'{indent}<b>{v}</b>'))
