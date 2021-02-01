#!/usr/bin/env python

import proton

if __name__ == '__main__':
    try:
        proton.main(branch='staging')
    except ValueError:
        print('No pre-release branch found.')

