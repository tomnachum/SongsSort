class Logger:
    def __init__(self, debug_enabled: bool):
        self.debug_enabled = debug_enabled

    def _print_helper(self, message, artist='', track='', **kwargs):
        to_print = message
        if artist and track:
            to_print += ' ' * (50 - len(message)) + f' {artist} - {track}'
        if kwargs:
            for key, val in kwargs.items():
                val_print = ''
                if isinstance(val, list):
                    for e in val:
                        val_print += '\n\t\t' + str(e)
                else:
                    val_print = val
                to_print += f'\n\t{key} = {val_print}'
        return to_print

    def error(self, message, **kwargs):
        print("\033[91m {}\033[00m".format(self._print_helper(f'\nERROR: {message}', **kwargs)))

    def success(self, message, **kwargs):
        print("\033[92m {}\033[00m".format(self._print_helper(f"\nSUCCESS: {message}", **kwargs)))

    def info(self, message, **kwargs):
        print(self._print_helper(f"\nINFO: {message}", **kwargs))

    def debug(self, message, **kwargs):
        if self.debug_enabled:
            print(self._print_helper(f"\nTEST: {message}", **kwargs))

    def warning(self, message, **kwargs):
        print("\033[38;5;208m{}\033[0m".format(self._print_helper(f'\nWARNING: {message}', **kwargs)))
