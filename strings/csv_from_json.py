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
        [], [], [],
        ['', f'English (original - {english_author})', f'Dutch ({dutch_translator})', f'French ({french_translator})'],
        [],
    ])

    for category in ('items', 'containers', 'rooms'):
        # first category header and desc_stem
        w.writerows([
            [category.title()],
            [],
            ['desc_stem', source['game'][category]['desc_stem']],
            [],
        ])

        # first category content
        for key, values in source['game'][category].items():
            if not isinstance(values, dict):
                continue

            for field in ('name', 'desc'):
                # proper names don't need to be translated
                if field == 'name':
                    if values.get('proper_name') == values['name'].title():
                        continue

                w.writerow([f'{key}/{field}', values[field]])
            w.writerow([])

        w.writerow([])

    # player strings
    w.writerows([
        ['Player'],
        [],
        ['player/name_default', source['game']['player']['name_default']],
        [],
    ])
