import time
import random
import urllib.request
import urllib.error

from datetime import datetime
# from tkinter import *


# todo: update this to match the discord version?
__version__ = '5.x.x'


# for recursion
def run_game():
    def n():
        print('')

    skip = False

    # typing output effects
    def stutter(text, delay=lambda: random.randint(1, 3)/100):
        if skip:
            print(text)
        else:
            for z in text:
                print(z, end='')
                time.sleep(delay())
            n()

    def stutters(text):
        stutter(text, delay=lambda: random.randint(5, 10)/100)

    def stutterf(text):
        stutter(text, lambda: 0.01)

    def stutterl(text):
        nonlocal skip
        skip_cached = skip
        skip = False
        stutter(text)
        skip = skip_cached

    inventory = dict()

    # list of commands for help
    help_info = [
        'help -Shows a list of commands',
        'skip -Toggles stuttering off',
        'noskip -Toggles stuttering on',
        'look around -Tells you what is in the room',
        'show inventory -Tells you what is in your inventory',
        'search [object] -Tells you what is in a container',
        'take [item] -Puts an item in your inventory',
        'take all -Puts all available items in your inventory',
        'use [item] -Lets you exercise the functionality of an item',
        'leave [place] -Lets you leave where you are',
        'go through [direction] port -Travel into adjacent modules',
        'drop [item] -Removes an item from your inventory',
        'quit -Ends the game',
        'Note:',
        'You can also use abbreviations for some commands.',
    ]

    functions = list()

    # npc interact subroutines
    def talktocrewmate():
        stutter('Hello there! Glad to see you got that malfunctioning hatch open.')
    
    # item use subroutines
    def usepaper():
        stutter('The strip of paper has a password on it.')
        stutter("'Pa$$word123'")
        stutter('You wonder what it is the password to.')
        stutter("(That's your cue to wonder what it is the password to)")

    def usedrive():
        if 'laptop' in inventory or 'laptop' in Room['Items']:
            if 'Files' in Drive:
                stutter('You transfer all the files on the usb stick to the laptop.')
                Laptop['Files'] = Drive['Files']
                del Drive['Files']
            else:
                stutter('There are no files on the usb stick.')
        else:
            stutter('You have to laptop to use it with.')

    def usejumpsuit():
        stutter('You put on the jumpsuit.')
        Player['Wearing'] = 'RussianJumpsuit'
        stutter('You were already wearing one, however, so you are now wearing two jumpsuits.')
        stutter('Good job.')

    def usegreenhouse():
        stutter('You watch the sprouts.')
        stutters('Nothing interesting happens.')

    def usecamera():
        if 'Windows' in Room:
            stutterl('You take the camera to a window and, after fiddling with '
                     'lenses and settings for\na few minutes, take a ')
            picture_quality = random.randint(1, 10)
            if picture_quality <= 2:
                picture_type = 'rubbish'
            elif picture_quality <= 5:
                picture_type = 'nice'
            else:
                picture_type = 'beautiful'
            picture_name = f'{picture_type} picture'
            stutter(f'{picture_name}.')
            inventory[picture_name] = picture_quality
        else:
            stutter('There are no windows to take pictures out of in this module.')

    def usetoilet():
        stutter("You do your business in the space toilet. Don't ask an astronaut "
                "how this \nhappens if you meet one, they're tired of the question.")

    def usebed():
        stutter("You get in the 'bed'.")
        if Player['Sleep'] > 8:
            stutter('You sleep until you are no longer tired.')
            nonlocal FicEpoch
            FicEpoch += Player['Sleep'] * 3600
            Player['Sleep'] = 0
            stutter('Date: ' + datetime.fromtimestamp(FicEpoch).strftime('%d.%m.%Y'))
        else:
            stutter('You are not tired enough to get to sleep.')

    def uselaptop():
        if Laptop['Tutorial'] == 'Pending':
            stutter('There is a sticker on the laptop that lists things you can do with it.')
            stutterf('browse web')
            stutterf('use messenger app')
            stutterf('read files')
            stutterf('play text game')
            stutterf('control station module')
            Laptop['Tutorial'] = 'Complete'
            n()
        stutter('You turn on the laptop.')
        Laptop['State'] = 'On'
        while Laptop['State'] == 'On':
            n()
            task = input()
            log(task)
            n()

            if 'turn off' in task:
                stutter('You turn off the laptop.')
                Laptop['State'] = 'Off'

            elif task == 'browse web':
                stutter('A browser window opens. Where do you want to go?')
                url = input()
                log(url)
                try:
                    response = urllib.request.urlopen(url)
                    html = response.read()
                    print(html)
                    stutter("Hmm, looks like there's no GUI.")
                    stutter('Oh well.')
                except ValueError:
                    stutter("That's not a valid URL.")
                except urllib.error.URLError:
                    stutter('You have no internet connection.')

            elif task == 'read files':
                if Laptop['Files'] == 'None':
                    stutter('You have no files to read!')
                else:
                    stutter('The files say: ')
                    stutter(Laptop['Files'])

            elif task == 'use messenger app':
                contacts = ['nasa social media team']
                stutter('In your contacts list are: ')
                for contact in contacts:
                    stutterf(contact)

                stutter('Who would you like to message?')
                invalid_input = True
                while invalid_input:
                    contact = input()
                    log(contact)
                    if contact in contacts:
                        invalid_input = False
                        if contact == 'nasa social media team':
                            stutter('You can send pictures to NASA to be posted online.')
                            stutter('What picture would you like to send?')
                            picture = input()
                            log(picture)
                            if 'picture' in picture:
                                if picture in inventory:
                                    stutter('You send the picture.')
                                    likes = inventory[picture] * random.randint(10, 1000)
                                    stutter('Your picture gets ' + str(likes) + ' likes.')
                                    del inventory[picture]
                                else:
                                    stutter("You don't have that picture.")
                            else:
                                stutter("That's not a picture!")
                    else:
                        stutter("They aren't in your contacts list.")

            elif task == 'play text game':
                run_game()

            elif task == 'control station module':
                stutter('A window opens with a few readouts and options.')
                stutter('periapsis: 390km')
                stutter('apoapsis: 390km')
                stutter('inclination: 51.6°')
                stutter('orbital period: 93 minutes')
                stutter('thruster statuses: nominal')
                stutter('alignment: retrograde')
                stutter("There is a button that says 'fire main engines'.")
                stutter('Would you like to press it?')
                choice = input()
                log(choice)
                if 'yes' in choice:
                    stutter('You press the button and tons of Gs force you against the back of the module.')
                    stutter("This is a cargo module, which means there's no seat to help you.")
                    stutter('Your orbit is rapidly falling deeper into the atmosphere.')
                    stutter('The remains of the module hits the ground at terminal velocity.')
                    stutter("But it's ok, because you were already obliterated "
                            'when its unshielded mass burnt up violently in the atmosphere.')
                    stutters('GAME OVER')
                    Carry['On'] = False
                    input()
                    break
                else:
                    stutter('That was probably a sensible choice.')

            else:
                stutter("The laptop can't do that!")

    # items
    Laptop = {'Name': 'Laptop', 'Desc': ' a laptop on the wall.',
              'Usable': 'Yes', 'Takeable': 'Yes',
              'State': 'Off', 'Tutorial': 'Pending', 'Files': 'None'}

    Paper = {'Name': 'Paper', 'Desc': ' a strip of paper.',
             'Usable': 'Yes', 'Takeable': 'Yes'}
    Drive = {'Name': 'Drive', 'Desc': ' a usb stick.',
             'Usable': 'Yes', 'Takeable': 'Yes',
             'Files': "'print('hello world!')'"}
    Jumpsuit = {'Name': 'Jumpsuit',
                'Desc': ' a blue jumpsuit with the flag of THE GLORIOUS SOVIET UNION I mean, Russia, on it.',
                'Usable': 'Yes', 'Takeable': 'Yes'}

    Greenhouse = {'Name': 'Lada',
                  'Desc': ' a little greenhouse thing with sprouts growing in it.',
                  'Usable': 'Yes'}
    Camera = {'Name': 'Camera', 'Desc': ' a DSLR camera and a few lenses on the wall.',
              'Usable': 'Yes', 'Takeable': 'Yes'}
    Toilet = {'Name': 'Space Toilet', 'Desc': ' a bogstandard space toilet in a little cubicle. Pun intended.',
              'Usable': 'Yes'}
    Bed = {'Name': 'Sleeping Bag',
           'Desc': ' a simple sleeping bag strapped securely to a wall.',
           'Usable': 'Yes'}

    # objects
    ContainersItems = {'paper': Paper, 'drive': Drive, 'jumpsuit': Jumpsuit}
    Containers = {'Name': 'Containers', 'Items': ContainersItems,
                  'Leavable': 1,
                  'Desc': 'looking in the containers lining the walls.'}

    # rooms
    ZaryaPorts = {'front': 'open', 'nadir': 'closed', 'aft': 'open'}
    ZaryaNear = {'front': 'Unity', 'aft': 'Zvezda'}
    ZaryaItems = {'laptop': Laptop}
    ZaryaObjects = {'containers': Containers}
    Zarya = {
        'Name': 'Zarya', 'Leavable': 0,
        'Ports': ZaryaPorts, 'Near': ZaryaNear,
        'Items': ZaryaItems, 'Objects': ZaryaObjects,
        'Desc': 'in a bland white module, what may sometimes be considered the walls \nlined with storage ' 
                'containers.'
    }

    UnityPorts = {
        'front': 'closed', 'nadir': 'closed',
        'port': 'closed', 'zenith': 'closed',
        'starboard': 'closed', 'aft': 'open'
    }
    UnityNear = {'aft': 'Zarya'}
    UnityItems = dict()
    UnityObjects = dict()
    Unity = {
        'Name': 'Unity', 'Leavable': 0,
        'Ports': UnityPorts, 'Near': UnityNear,
        'Items': UnityItems, 'Objects': UnityObjects,
        'Desc': 'in one of the nodes that links part of the station. '
    }

    ZvezdaPorts = {
        'front': 'open', 'nadir': 'closed',
        'zenith': 'closed', 'aft': 'closed'
    }
    ZvezdaNear = {'front': 'Zarya'}
    ZvezdaItems = {'greenhouse': Greenhouse, 'camera': Camera, 'toilet': Toilet,
                   'bed': Bed}
    ZvezdaObjects = dict()
    Zvezda = {
        'Name': 'Zvezda', 'Leavable': 0, 'Windows': 'Yes',
        'Ports': ZvezdaPorts, 'Near': ZvezdaNear,
        'Items': ZvezdaItems, 'Objects': ZvezdaObjects,
        'Desc': "in a three-part service module, with a spherical 'Transfer "
                "Compartment' to the front, a 'Work Compartment' with living "
                'quarters and life support, where things are done, and to aft a '
                "'Transfer Chamber'."
    }

    # player
    Player = {'Name': 'Player', 'Wearing': 'Jumpsuit',
              'Inventory': inventory, 'Images': 0, 'Sleep': 5}

    # def helpwindow():
    #     helpw = Tk()
    #     helpw.title('help')
    #     helpc = Canvas(helpw, height=(len(help_info)*20)+20, width=650)
    #     helpc.pack()
    #     text = list()
    #     for help_info_item in help_info:
    #         text.append(helpc.create_text(325, (i*20)+20, text=help_info_item))

    Months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # start game
    Room = Zarya
    FicEpoch = 968716800
    stutterf(f'Zarya v{__version__}')
    stutterf('© Joel McBride 2017, 2021')
    stutterf("Remember to report any bugs or errors to 'joel.mcbride1@live.com'.")
    n()
    stutter('Date: ' + datetime.fromtimestamp(FicEpoch).strftime('%d.%m.%Y'))
    stutter("For a list of commands, type 'help'.")

    # command reader
    Carry = {'On': True}
    while Carry['On']:
        Player['Sleep'] += 1
        FicEpoch += 3600
        n()
        Do = str.lower(input())
        log(Do)
        n()

        if Do in ['help', 'h']:
            for help_info_item in help_info:
                stutterf(help_info_item)
            stutter('For the uninitiated: ')
            stutter('In text-based adventure games, a good first command when '
                    "starting out or \nentering a new place is 'look around'.")

        elif Do in ['quit', 'q']:
            break

        elif Do in ['look around', 'look', 'la', 'l']:
            stutter('You are ' + Room['Desc'] + ' ')
            Items = Room['Items']
            if len(Items) > 0:
                ItemVars = list(Items.values())
                for i, value in enumerate(Items):
                    stutter(f"There is{ItemVars[i]['Desc']}")
            if 'Ports' in Room:
                stutter('There are ' + str(len(Room['Ports'])) + ' ports: ')
                Ports = Room['Ports']
                PortTypes = list(Ports.keys())
                PortStates = list(Ports.values())
                for i, value in enumerate(Room['Ports']):
                    stutter(f'One to {PortTypes[i]} that is {PortStates[i]}.')

        elif Do in ['show inventory', 'inventory', 'si', 'i']:
            if not inventory:
                stutter('Your inventory is empty.')
            else:
                you_have = list(inventory)
                stutter('In your inventory is: ')
                for inventory_item in inventory:
                    stutter(you_have[inventory_item])

        elif 'search' in Do:
            Object = Do[7:]
            if Object in Room['Objects']:
                PrevRoom = Room
                stutter(f'You search the {Object}.')
                ObjectIndx = Room['Objects']
                Room = ObjectIndx[Object]
                Items = list(Room['Items'])
                if len(Items) > 0:
                    stutter(f'The {Object} contain(s):')
                    for item in Items:
                        stutter(item)
                else:
                    stutter("There isn't anything here.")
            else:
                stutter("That isn't in here.")

        elif 'leave' in Do:
            if Room['Leavable'] == 1:
                stutter('You leave the ' + str.lower(Room['Name']) + '.')
                Room = PrevRoom
            else:
                stutter(f"I'm sorry {Player['Name']}, I'm afraid you can't do that.")

        elif 'go through' in Do or 'gt' in Do or 'go' in Do:
            if 'go through' in Do and 'port' in Do:
                SubStringEnd = Do.index('port')
                SubStringEnd = SubStringEnd - 1
                Direction = Do[11:SubStringEnd]
            elif 'go through' in Do:
                Direction = Do[11:]
            elif 'gt' in Do and 'p' in Do:
                SubStringEnd = Do.index('p')
                SubStringEnd = SubStringEnd - 1
                Direction = Do[3:SubStringEnd]
            elif 'gt' in Do or 'go' in Do:
                Direction = Do[3:]
            if Direction in Room['Ports']:
                Ports = Room['Ports']
                if Ports[Direction] == 'open':
                    Near = Room['Near']
                    NextRoom = Near[Direction]
                    stutter('You go through the port into ' + NextRoom + '.')
                    Room = eval(Near[Direction])
                else:
                    stutter('That port is closed.')
            else:
                stutter("The module you're in doesn't have a port there.")

        elif Do in ['take all', 'ta']:
            ItemsList = list(Room['Items'])
            if len(ItemsList) > 0:
                stutter('You: ')
                stutter('TAKE ')
                stutter('ALL THE THINGS.')
                Items = Room['Items']
                for i, value in enumerate(Items):
                    Item = ItemsList[i]
                    TrueItem = str.upper(Item[0]) + Item[1:]
                    if 'Takeable' in eval(TrueItem):
                        Details = Items[Item]
                        inventory[Item] = Details
                        del Items[Item]
                    else:
                        stutter(f"You can't take the {Item}.")
            else:
                stutter("There's nothing here.")

        elif 'take' in Do:
            Item = Do[5:]
            Items = Room['Items']
            Details = Items[Item]
            if Item in Items:
                TrueItem = str.upper(Item[0]) + Item[1:]
                if 'Takeable' in eval(TrueItem):
                    stutter('You take the ' + Item + '.')
                    inventory[Item] = Details
                    del Items[Item]
                else:
                    stutter("You can't take that.")
            else:
                stutter("That item isn't here.")

        elif 'use' in Do:
            Item = Do[4:]
            if Item in inventory or Item in Room['Items']:
                TrueItem = str.upper(Item[0]) + Item[1:]
                if 'Usable' in eval(TrueItem):
                    SubCall = 'use' + str(Item) + '()'
                    eval(SubCall)
                else:
                    stutter("That item isn't usable.")
            else:
                stutter("You don't have that item.")

        elif 'drop' in Do:
            Item = Do[5:]
            if Item in inventory:
                stutter('You drop the ' + Item + '.')
                Items = Room['Items']
                Details = inventory[Item]
                Items[Item] = Details
                del inventory[Item]
            else:
                stutter("That item isn't in your inventory.")

        elif Do in ['skip', 's']:
            skip = True
            stutter('Text will now output instantly.')

        elif Do in ['noskip', 'ns', 'n']:
            skip = False
            stutter('Text will now output gradually.')

        elif Do.startswith('setname'):
            new_name = Do.removeprefix('setname').strip()
            Player['Name'] = new_name
            stutter(f"Your name is {Player['Name']}.")

        else:
            stutter("That's not a valid command.")


# logging
def log(text):
    with open('log.txt', 'a+') as log_file:
        log_file.write('\n' + str(text))


if __name__ == '__main__':
    # log new game
    log('\n')
    log('hello world!')
    log(str(datetime.now()))

    # run
    run_game()
