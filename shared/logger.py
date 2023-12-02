class Logger:
    def __init__(self, is_test: bool):
        self.is_test = is_test

    def _print_helper(self, message, artist='', track='', **kwargs):
        to_print = message
        if artist and track:
            to_print += ' ' * (50 - len(message)) + f' {artist} - {track}'
        if kwargs:
            for key, val in kwargs.items():
                val_print = ''
                if isinstance(val, list):
                    for e in val:
                        val_print += '\n\t\t' + e
                else:
                    val_print = val
                to_print += f'\n\t{key} = {val_print}'
        return to_print

    def error(self, message, **kwargs):
        print("\033[91m {}\033[00m".format(self._print_helper(f'ERROR: {message}', **kwargs)))

    def success(self, message, **kwargs):
        print("\033[92m {}\033[00m".format(self._print_helper(message, **kwargs)))

    def info(self, message, **kwargs):
        print(self._print_helper(f"INFO: {message}", **kwargs))

    def test(self, message, **kwargs):
        if self.is_test:
            print(self._print_helper(f"TEST LOG: {message}", **kwargs))

    def warning(self, message, **kwargs):
        print("\033[38;5;208m{}\033[0m".format(self._print_helper(f'WARNING: {message}', **kwargs)))
