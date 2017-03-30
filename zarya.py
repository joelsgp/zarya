from random import randint
from time import sleep
from urllib import request
from datetime import datetime

#for recursion
def rungame():
    #newline
    def n():
        print('')

    Skip = False

    #typing output effects
    def stutter(Text):
        for z in range (len(Text)):
            if Skip == True:
                print(Text, end='')
                break
            print(Text[z], end='')
            sleep(randint(1,3)/100)
        print('')

    def stutters(Text):
        for z in range (len(Text)):
            if Skip == True:
                print(Text, end='')
                break
            print(Text[z], end='')
            sleep(randint(5,10)/100)
        print('')

    def stutterf(Text):
        for z in range (len(Text)):
            if Skip == True:
                print(Text, end='')
                break
            print(Text[z], end='')
            sleep(0.01)
        print('')

    def stutterl(Text):
        for z in range (len(Text)):
            if Skip == True:
                print(Text, end='')
                break
            print(Text[z], end='')
            sleep(randint(1,3)/100)

    Inventory = dict()

    #list of commands for help
    Help = list()
    Functions = list()
    Help.append('help -Shows a list of commands')
    Help.append('skip -Toggles stuttering off')
    Help.append('noskip -Toggles stuttering on')
    Help.append('look around -Tells you what is in the room')
    Help.append('show inventory -Tells you what is in your inventory')
    Help.append('search [object] -Tells you what is in a container')
    Help.append('take [item] -Puts an item in your inventory')
    Help.append('take all -Puts all available items in your inventory')
    Help.append('use [item] -Lets you excersise the funtionality of an item')
    Help.append('leave [place] -Lets you leave where you are')
    Help.append('go through [direction] port -Travel into adjacent modules')
    Help.append('drop [item] -Removes an item from your inventory')
    Help.append('quit -Ends the game')
    Help.append('Note:')
    Help.append('You can also use abbrevitations for some commands.')

    #item use subroutines
    def usepaper():
        stutter('The strip of paper has a password on it.')
        stutter('\'Pa$$word123\'')
        stutter('You wonder what it is the password to.')
        stutter('(That\'s your cue to wonder what it is the password to)')

    def usedrive():
        if 'laptop' in Inventory or 'laptop' in Room['Items']:
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
        stutter('You were already wearing one, however, ' \
                'so you are now wearing two jumpsuits.')
        stutter('Good job.')

    def usegreenhouse():
        stutter('You watch the sprouts.')
        stutters('Nothing interesting happens.')

    def usecamera():
        if 'Windows' in Room:
            stutterl('You take the camera to a window and, after fiddling with ' \
                    'lenses and settings for\na few minutes, take a ')
            PictureQuality = randint(1, 10)
            if PictureQuality <= 2:
                PictureType = 'rubbish'
            elif PictureQuality <= 5:
                PictureType = 'nice'
            else:
                PictureType = 'beautiful'
            Name = str(PictureType + ' picture')
            stutter(Name + '.')
            Inventory[Name] = PictureQuality
        else:
            stutter('There are no windows to take pictures out of in this module.')

    def usetoilet():
        stutter('You do your business in the space toilet. Don\'t ask an astronaut ' \
                'how this \nhappens if you meet one, they\'re tired of the question.')

    def usebed():
        stutter('You sleep till \'morning\'.')
        nonlocal FicEpoch
        FicEpoch += 86400
        stutter('Date: ' + datetime.fromtimestamp(FicEpoch).strftime('%d.%m.%Y'))

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
            Task = input()
            log(Task)
            n()
            if 'turn off' in Task:
                stutter('You turn off the laptop.')
                Laptop['State'] = 'Off'
            elif Task == 'browse web':
                stutter('A browser window opens. Where do you want to go?')
                URL = input()
                log(URL)
                try:
                    response = request.urlopen(URL)
                    html = response.read()
                    print(html)
                    stutter('Hmm, looks like there\'s no GUI.')
                    stutter('Oh well.')
                except ValueError as err:
                    stutter('That\'s not a valid URL.')
                except urllib.error.URLError as err:
                    stutter('You have no internet connection.')
            elif Task == 'read files':
                if Laptop['Files'] == 'None':
                    stutter('You have no files to read!')
                else:
                    stutter('The files say: ')
                    stutter(Laptop['Files'])
            elif Task == 'use messenger app':
                Contacts = ['nasa social media team']
                stutter('In your contacts list are: ')
                for i in range (len(Contacts)):
                    stutterf(Contacts[i])
                stutter('Who would you like to message?')
                NotRight = True
                while NotRight == True:
                    Contact = input()
                    log(Contact)
                    if Contact in Contacts:
                        NotRight = False
                        if Contact == 'nasa social media team':
                            stutter('You can send pictures to NASA to be posted online.')
                            stutter('What picture would you like to send?')
                            Picture = input()
                            log(Picture)
                            if 'picture' in Picture:
                                if Picture in Inventory:
                                    stutter('You send the picture.')
                                    Likes = Inventory[Picture] * randint(10, 1000)
                                    stutter('Your picture gets ' + str(Likes) + ' likes.')
                                    del Inventory[Picture]
                                else:
                                    stutter('You don\'t have that picture.')
                            else:
                                stutter('That\'s not a picture!')
                    else:
                        stutter('They aren\'t in your contacts list.')
            elif Task == 'play text game':
                rungame()
            elif Task == 'control station module':
                stutter('A window opens with a few readouts and options.')
                stutter('periapsis: 390km')
                stutter('apoapsis: 390km')
                stutter('inclination: 51.6°')
                stutter('orbital period: 93 minutes')
                stutter('thruster statuses: nominal')
                stutter('alignment: retrograde')
                stutter('There is a button that says \'fire main engines\'.')
                stutter('Would you like to press it?')
                Choice = input()
                log(Choice)
                if 'yes' in Choice:
                    stutter('You press the button and tons of Gs force you against the back of the module.')
                    stutter('This is a cargo module, which means there\'s no seat to help you.')
                    stutter('Your orbit is rapidly falling deeper into the atmosphere.')
                    stutter('The remains of the module hits the ground at terminal velocity.')
                    stutter('But it\'s ok, because you were already obliterated '\
                            'when its unsheilded mass burntup violently in the atmosphere.')
                    stutters('GAME OVER')
                    Carry['On'] = False
                    Delay = input()
                    break
                else:
                    stutter('That was probably a sensible choice.')
            else:
                stutter('The laptop can\'t do that!')

    #items
    Laptop = {'Name': 'Laptop', 'Desc': ' a laptop on the wall.',
              'Usable': 'Yes', 'Takeable': 'Yes',
              'State': 'Off', 'Tutorial': 'Pending', 'Files': 'None'}

    Paper = {'Name': 'Paper', 'Desc': ' a strip of paper.',
             'Usable': 'Yes', 'Takeable': 'Yes'}
    Drive = {'Name': 'Drive', 'Desc': ' a usb stick.',
             'Usable': 'Yes', 'Takeable': 'Yes',
             'Files': '\'print(\'hello world!\')\''}
    Jumpsuit = {'Name': 'Jumpsuit', 'Desc': ' a blue jumpsuit with the flag '\
                'of THE GLORIOUS SOVIET UNION I mean, Russia, on it.',
                'Usable': 'Yes', 'Takeable': 'Yes'}

    Greenhouse = {'Name': 'Lada', 'Desc': ' a little greenhouse thing ' \
                  'with sprouts growing in it.',
                  'Usable': 'Yes'}
    Camera = {'Name': 'Camera', 'Desc': ' a dslr camera and a few lenses ' \
              'on the wall.',
              'Usable': 'Yes', 'Takeable': 'Yes'}
    Toilet = {'Name': 'Space Toilet', 'Desc': ' a bogstandard space toilet ' \
              'in a little cubicle.',
              'Usable': 'Yes'}
    Bed = {'Name': 'Sleeping Bag', 'Desc': ' a simple sleeping bag strapped ' \
              'securely to a wall.',
              'Usable': 'Yes'}

    #objects
    ContainersItems = {'paper': Paper, 'drive': Drive, 'jumpsuit': Jumpsuit}
    Containers = {'Name': 'Containers', 'Items': ContainersItems,
                  'Leavable': 1,
                  'Desc': 'looking in the containers lining the walls.'}

    #rooms
    ZaryaPorts = {'front': 'open', 'nadir': 'closed', 'aft': 'open'}
    ZaryaNear = {'front': 'Unity', 'aft': 'Zvezda'}
    ZaryaItems = {'laptop': Laptop}
    ZaryaObjects = {'containers': Containers}
    Zarya = {'Name': 'Zarya', 'Leavable': 0,
             'Ports': ZaryaPorts, 'Near': ZaryaNear,
             'Items': ZaryaItems, 'Objects': ZaryaObjects,
             'Desc': 'in a bland white module, what may ' \
             'sometimes be considered the walls \nlined with storage ' \
             'containers.'}

    UnityPorts = {'front': 'closed', 'nadir': 'closed',
                  'port': 'closed', 'zenith': 'closed',
                  'starboard': 'closed', 'aft': 'open'}
    UnityNear = {'aft': 'Zarya'}
    UnityItems = dict()
    UnityObjects = dict()
    Unity = {'Name': 'Unity', 'Leavable': 0,
             'Ports': UnityPorts, 'Near': UnityNear,
             'Items': UnityItems, 'Objects': UnityObjects,
             'Desc': 'in one of the nodes that links part of the station. '}

    ZvezdaPorts = {'front': 'open', 'nadir': 'closed',
                   'zenith': 'closed', 'aft': 'closed'}
    ZvezdaNear = {'front': 'Zarya'}
    ZvezdaItems = {'greenhouse': Greenhouse, 'camera': Camera, 'toilet': Toilet,
                   'bed': Bed}
    ZvezdaObjects = dict()
    Zvezda = {'Name': 'Zvezda', 'Leavable': 0, 'Windows': 'Yes',
             'Ports': ZvezdaPorts, 'Near': ZvezdaNear,
             'Items': ZvezdaItems, 'Objects': ZvezdaObjects,
             'Desc': 'in a three-part service module, with a spherical \'Transfer ' \
              'Compartment\' to the front, a \'Work Compartment\' with living ' \
              'quarters and life support, where things are done, and to aft a ' \
              '\'Transfer Chamber\'.'}

    #player
    Player = {'Name': 'Player', 'Wearing': 'Jumpsuit',
              'Inventory': Inventory, 'Images': 0}

    def helpwindow():
        helpw = Tk()
        helpw.title('help')
        helpc = Canvas(helpw, height = (len(Help)*20)+20, width = 650)
        helpc.pack()
        Text = list()
        for i in range (len(Help)):
            Text.append(helpc.create_text(325, (i*20)+20, text=Help[i]))

    Months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

    #start game
    Room = Zarya
    FicEpoch = 968716800
    stutterf('Zarya v4')
    stutterf('© Joel McBride 2017')
    stutterf('Remember to report any bugs or errors to \'jmcbri14@st-pauls.leicester.sch.uk.\'')
    n()
    stutter('Date: ' + datetime.fromtimestamp(FicEpoch).strftime('%d.%m.%Y'))
    stutter('For a list of commands, type \'help\'.')
    #command reader
    Carry = {'On': True}
    while Carry['On'] == True:
        n()
        Do = str.lower(input())
        log(Do)
        n()
        if Do == 'help' or Do == 'h':
            for i in range (len(Help)):
                stutterf(Help[i])
            stutter('For the uninitiated: ')
            stutter('In text-based adventure games, a good first command when ' \
                    'starting out or \nentering a new place is \'look around\'.')
        elif Do == 'quit' or Do == 'q':
            break
        elif Do == 'look around' or Do == 'look' or Do == 'la' or Do == 'l':
            stutter('You are ' + Room['Desc'] + ' ')
            Items = Room['Items']
            if len(Items) > 0:
                ItemVars = list(Items.values())
                for i in range (len(Items)):
                    Item = ItemVars[i]
                    stutter('There is' + Item['Desc'])
            if 'Ports' in Room:
                stutter('There are ' + str(len(Room['Ports'])) + ' ports: ')
                Ports = Room['Ports']
                PortTypes = list(Ports.keys())
                PortStates = list(Ports.values())
                for i in range (len(Room['Ports'])):
                    stutter('One to ' + PortTypes[i] + ' that is ' + PortStates[i] + '.')
        elif Do == 'show inventory' or Do == 'inventory' or Do == 'si' or Do == 'i':
            if len(Inventory) == 0:
                stutter('Your inventory is empty.')
            else:
                YouHave = list(Inventory)
                stutter('In your inventory is: ')
                for i in range (len(Inventory)):
                    stutter(YouHave[i])
        elif 'search' in Do:
            Object = Do[7:]
            if Object in Room['Objects']:
                PrevRoom = Room
                stutter('You search the ' + Object + '.')
                ObjectIndx = Room['Objects']
                Room = ObjectIndx[Object]
                Items = list(Room['Items'])
                if len(Items) > 0:
                    stutter('The ' + Object + ' contain(s):')
                    for i in range (len(Items)):
                        stutter(Items[i])
                else:
                    stutter('There isn\'t anything here.')
            else:
                stutter('That isn\'t in here.')
        elif 'leave' in Do:
            if Room['Leavable'] == 1:
                stutter('You leave the ' + str.lower(Room['Name']) + '.')
                Room = PrevRoom
            else:
                stutter('I\'m sorry ' + Player['Name'] + ', you can\'t do that.')
        elif 'go through' in Do or 'gt' in Do:
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
            elif 'gt' in Do:
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
                stutter('The module you\'re in doesn\'t have a port there.')
        elif Do == 'take all' or Do == 'ta':
            ItemsList = list(Room['Items'])
            if len(ItemsList) > 0:
                stutter('You: ')
                stutter('TAKE ')
                stutter('ALL THE THINGS.')
                Items = Room['Items']
                for i in range (len(Items)):
                    Item = ItemsList[i]
                    TrueItem = str.upper(Item[0]) + Item[1:]
                    if 'Takeable' in eval(TrueItem):
                        Details = Items[Item]
                        Inventory[Item] = Details
                        del Items[Item]
                    else:
                        stutter('You can\'t take the ' + Item + '.')
            else:
                stutter('There\'s nothing here.')
        elif 'take' in Do:
            Item = Do[5:]
            Items = Room['Items']
            Details = Items[Item]
            if Item in Items:
                TrueItem = str.upper(Item[0]) + Item[1:]
                if 'Takeable' in eval(TrueItem):
                    stutter('You take the ' + Item + '.')
                    Inventory[Item] = Details
                    del Items[Item]
                else:
                    stutter('You can\'t take that.')
            else:
                stutter('That item isn\'t here.')
        elif 'use' in Do:
            Item = Do[4:]
            if Item in Inventory or Item in Room['Items']:
                TrueItem = str.upper(Item[0]) + Item[1:]
                if 'Usable' in eval(TrueItem):
                    SubCall = 'use' + str(Item) + '()'
                    eval(SubCall)
                else:
                    stutter('That item isn\'t usable.')
            else:
                stutter('You don\'t have that item.')
        elif 'drop' in Do:
            Item = Do[5:]
            if Item in Inventory:
                stutter('You drop the ' + Item + '.')
                Items = Room['Items']
                Details = Inventory[Item]
                Items[Item] = Details
                del Inventory[Item]
            else:
                stutter('That item isn\'t in your inventory.')
        elif Do == 'skip' or Do == 's':
            Skip = True
            stutter('Text will now output instantly.')
        elif Do == 'noskip' or Do == 'n' or Do == 'ns':
            Skip = False
            stutter('Text will now output gradually.')
        else:
            stutter('That\'s not a valid command.')

#logging
def log(Text):
    LogFile = open('log.txt', 'a+')
    LogFile.write('\n' + str(Text))
    LogFile.close()
#log newgame
log('\n')
log('hello world!')
log(str(datetime.now()))

try:
    rungame()
    quit()
except:
    import sys
    err = sys.exc_info()
    if not 'SystemExit' in str(err):
        log(err)
        print('ERROR')
        print(err)
        Delay = input()
