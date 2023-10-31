class Logger:
    def __init__(self, is_test: bool):
        self.is_test = is_test

    def _print_helper(self, message, artist_name='', track_name='', **kwargs):
        to_print = message
        if artist_name and track_name:
            to_print += ' ' * (50 - len(message)) + f' {artist_name} - {track_name}'
        if kwargs:
            for key, val in kwargs.items():
                to_print += f'\n\t{key} = {val}'
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
