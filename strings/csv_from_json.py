#!usr/bin/env python

import csv
import json


source_language = 'en'
english_author = 'JMcB#7918'
dutch_translator = 'Marcel D#0001'
french_translator = 'forevertoo#8663'


with open(f'{source_language}.json', 'r') as source_json_file:
    source = json.load(source_json_file)


# todo: change to mode x when done testing
with open('translations.csv', 'w', newline='') as csv_file:
    w = csv.writer(csv_file)

    # main header
    w.writerows([
        ['Key:'],
        ['desc_stem', 'Description stem, added to the start of every description.'],
        ['name', 'Name.'],
        ['desc', 'Description.'],
        [''],
        ['', f'English (original - {english_author})', f'Dutch {dutch_translator}', f'French ({french_translator})'],
        [''],
    ])

    # first category header and desc_stem
    w.writerows([
        ['Items'],
        [''],
        ['desc_stem', source['game']['items']['desc_stem']],
        [''],
    ])

    # first category content
    for item, values in source['game']['items'].items():
        if not isinstance(values, dict):
            continue

        for field in ('name', 'desc'):
            w.writerow([f'{item}/{field}', values[field]])
        w.writerow([''])
