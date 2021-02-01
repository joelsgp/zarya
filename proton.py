#!/usr/bin/env python

import os
import urllib.request
import urllib.error


__version__ = '0.10.0'


def download(branch='main'):
    blob_url = f'https://raw.githubusercontent.com/JMcB17/Zarya/{branch}/zarya.py'

    print(f'Downloading and executing code from {blob_url}')
    print('Connecting...')
    try:
        with urllib.request.urlopen(blob_url) as response:
            code = response.read()
            print('Latest version downloaded. \n')
            return code
    except urllib.error.URLError:
        print('No connection.')
        return None


def update(code):
    with open(os.path.join('game', 'zarya.py'), 'w') as file:
        file.write(code)


def run():
    import game.zarya as zarya
    game_instance = zarya.ZaryaGame()
    game_instance.log_start()
    game_instance.run()


# TODO: only update if needed
def main(branch='main'):
    print(f'Proton launcher for zarya v{__version__}')

    code = download(branch=branch)
    if code:
        update(code)
    else:
        print('Running existing version.')
    run()


if __name__ == '__main__':
    main()
