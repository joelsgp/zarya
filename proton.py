#!/usr/bin/env python

import urllib.request
import urllib.error


__version__ = '0.9.0'


def main(branch='main'):
    print(f'Proton launcher for zarya v{__version__}')
    blob_url = f'https://raw.githubusercontent.com/JMcB17/Zarya/{branch}/zarya.py'

    print(f'Downloading and executing code from {blob_url}')
    print('Connecting...')
    try:
        with urllib.request.urlopen(blob_url) as response:
            code = response.read()
            print('Latest version downloaded. \n')
            exec(code)
    except urllib.error.URLError:
        print('No connection.')


if __name__ == '__main__':
    main()
