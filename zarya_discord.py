import os
import json
import time
import random
import urllib.request
import urllib.error

from typing import List, Callable
# from tkinter import *

from discord_funcs import discord_input, discord_stutter


__version__ = '0.1.0'


# TODO: more comprehensive refactor, oop etc.


# need to make this dynamic
LANG = 'en'
# load strings
with open(os.path.join('strings', f'{LANG}.json')) as strings_file:
    STRINGS = json.load(strings_file)
# strings shortcuts
STRS_GAME = STRINGS['game']
STRS_ITEMS = STRS_GAME['items']
STRS_ROOMS = STRS_GAME['rooms']


class ZaryaItem:
    """Class for items.

    An item has a name and can be inspected for a description. It may be used, which will invoke usefunc, or taken.

    Attrs:
        name
        desc -- description of item
        can_use
        can_take
        usefunc -- function to be run when the item is used
    """
    desc_stem = STRS_ITEMS['desc_stem']

    def __init__(self, name: str, desc: str, can_use: bool = False, can_take: bool = False, usefunc: Callable = None):
        self.name = name
        if desc.startswith(self.desc_stem):
            desc = desc.removeprefix(self.desc_stem)
        self.desc = desc.strip()
        self.can_use = can_use
        self.can_take = can_take
        if self.can_use and usefunc is not None:
            self.usefunc = usefunc


# TODO: allow giving an identifier to the constructor to automatically get the name and desc from the strings file
class ZaryaContainer:
    """Class for containers.

    A container has a name, and a description which will be used when you `look` while inside it.
    It may be entered and exited, and contain items.

    Attrs:
        name
        desc -- look message of container
        can_leave -- whether you can leave the container, used in the ZaryaRoom subclass
        items -- items in the container, a list of ZaryaItems or None
    """

    desc_stem = STRS_GAME['containers']['desc_stem']

    def __init__(self, name: str, desc: str, can_leave: bool = True, items: List[ZaryaItem] = None):
        self.name = name
        if desc.startswith(self.desc_stem):
            desc = desc.removeprefix(self.desc_stem)
        self.desc = desc.strip()
        self.can_leave = can_leave
        if items is None:
            self.items = []
        else:
            self.items = items


class ZaryaPort:
    """Class for ports connecting two modules of the station (rooms).

    A port has a name, which should correspond to a direction in orbit, like the ones used to describe ISS ports.
    A port will be open or closed. If open, it may have a room which you will enter by going through it.
    If closed, trying to get the room attribute may raise an AttributeError.

    Attrs:
        name
        is_open
        room -- if applicable, the ZaryaRoom which you will enter by going through the port
    """
    def __init__(self, name: str, is_open: bool = False, room=None):
        self.name = name
        self.is_open = is_open
        if self.is_open and room is not None:
            self.room = room

    def __str__(self):
        return self.name


class ZaryaRoom(ZaryaContainer):
    """Class for rooms I.E. station modules.

    A room has all of a container's attributes. It may also have containers within it, and ports connecting it
    to other rooms.

    Attrs:
        desc -- look message of room
        can_leave -- whether you can leave the room, should be False
        has_windows -- determines whether the camera can be used in this room
        items -- items in the room, a list of ZaryaItems or None
        containers -- a list of ZaryaContainers which you can enter, or None
        ports -- a list of ZaryaPorts which may be open or closed, or None
    """
    def __init__(self, name: str, desc: str, can_leave: bool = False, has_windows: bool = False,
                 items: List[ZaryaItem] = None, containers: List[ZaryaContainer] = None, ports: List[ZaryaPort] = None):
        super().__init__(name, desc, can_leave, items)

        self.has_windows = has_windows
        if containers is None:
            self.containers = []
        else:
            self.containers = containers
        if ports is None:
            self.ports = []
        else:
            self.ports = ports

    def __str__(self):
        return self.name


class ZaryaPlayer:
    """Class for the player character.

    Attrs:
        name
        inventory --  a list of ZaryaItem's
        wearing -- outfit
        sleep -- how much sleep as a float
    """
    name = STRS_GAME['player']['name_default']

    def __init__(self, name: str, inventory: List[ZaryaItem], wearing, sleep: float = 5):
        self.name = name
        self.inventory = inventory
        self.wearing = wearing
        self.sleep = sleep

    def __str__(self):
        return self.name


class ZaryaGame:
    def __init__(self, discord_client, send_channel, req_channel_name=None):
        self.discord_client = discord_client
        self.send_channel = send_channel
        if req_channel_name is None:
            self.req_channel_name = ''
        else:
            self.req_channel_name = req_channel_name

    # newline function from old version - redundant now
    async def n(self):
        await discord_stutter('', channel=self.send_channel, skip=True)

    # typing output effects
    async def stutter(self, text, delay=lambda: random.randint(1, 3) / 100, skip=False):
        await discord_stutter(text, channel=self.send_channel, delay=delay, skip=skip)

    async def stutters(self, text, skip=False):
        await self.stutter(text, delay=lambda: random.randint(5, 10) / 100, skip=skip)

    async def stutterf(self, text, skip=False):
        await self.stutter(text, lambda: 0.01, skip=skip)

    async def stutterl(self, text):
        await self.stutter(text, skip=False)

    # item use subroutines
    async def use_paper(self):
        await self.stutter('The strip of paper has a password on it.')
        await self.stutter("'Pa$$word123'")
        await self.stutter('You wonder what it is the password to.')
        await self.stutter("(That's your cue to wonder what it is the password to)")

    async def use_drive(self):
        if 'laptop' in self.player.inventory or 'laptop' in self.current_room.items:
            if self.drive.files:
                await self.stutter('You transfer all the files on the usb stick to the laptop.')
                self.laptop.files = self.drive.files
                self.drive.files = []
            else:
                await self.stutter('There are no files on the usb stick.')
        else:
            await self.stutter('You have to laptop to use it with.')

    async def use_jumpsuit(self):
        await self.stutter('You put on the jumpsuit.')
        self.player.wearing = 'Russian jumpsuit'
        await self.stutter('You were already wearing one, however, so you are now wearing two jumpsuits.')
        await self.stutter('Good job.')

    async def use_greenhouse(self):
        await self.stutter('You watch the sprouts.')
        await self.stutters('Nothing interesting happens.')

    # TODO: fix bug with KeyError taking the camera
    # TODO: fix bug with using camera
    # TODO: combine string literals to help with rate limiting
    # TODO: move todos into relevant places :p
    async def use_camera(self):
        if self.current_room.has_windows:
            await self.stutterl('You take the camera to a window and, after fiddling with '
                                'lenses and settings for\na few minutes, take a ')
            picture_quality = random.randint(1, 10)
            if picture_quality <= 2:
                picture_type = 'rubbish'
            elif picture_quality <= 5:
                picture_type = 'nice'
            else:
                picture_type = 'beautiful'
            picture_name = f'{picture_type} picture'
            await self.stutter(f'{picture_name}.')
            self.player.inventory[picture_name] = picture_quality
        else:
            await self.stutter('There are no windows to take pictures out of in this module.')

    async def use_toilet(self):
        await self.stutter("You do your business in the space toilet. Don't ask an astronaut "
                           "how this \nhappens if you meet one, they're tired of the question.")

    async def use_bed(self):
        await self.stutter("You get in the 'bed'.")
        if self.player.sleep > 8:
            await self.stutter('You sleep until you are no longer tired.')
            self.posix_time_ingame += self.player.sleep * 3600
            self.player.sleep = 0
            await self.stutter(f"Date: {time.strftime('%d.%m.%Y', time.gmtime(self.posix_time_ingame))}")
        else:
            await self.stutter('You are not tired enough to get to sleep.')

    async def use_laptop(self):
        if self.laptop.tutorial == 'Pending':
            await self.stutter('There is a sticker on the laptop that lists things you can do with it.')
            await self.stutterf('browse web')
            await self.stutterf('use messenger app')
            await self.stutterf('read files')
            await self.stutterf('play text game')
            await self.stutterf('control station module')
            self.laptop.tutorial = 'Complete'
            await self.n()
        await self.stutter('You turn on the laptop.')
        self.laptop.state = 'On'
        while self.laptop.state == 'On':
            await self.n()
            task = await discord_input(self.discord_client, self.req_channel_name)
            self.log(task)
            await self.n()

            if task in 'turn off laptop':
                await self.stutter('You turn off the laptop.')
                self.laptop.state = 'Off'

            elif task in ['browse web', 'browse', 'web']:
                await self.stutter('A browser window opens. Where do you want to go?')
                url = await discord_input(self.discord_client, self.req_channel_name)
                self.log(url)
                try:
                    response = urllib.request.urlopen(url)
                    html = response.read()
                    print(html)
                    await self.stutter("Hmm, looks like there's no GUI.")
                    await self.stutter('Oh well.')
                except ValueError:
                    await self.stutter("That's not a valid URL.")
                except urllib.error.URLError:
                    await self.stutter('You have no internet connection.')

            elif task in ['read files', 'read', 'files']:
                if not self.laptop.files:
                    await self.stutter('You have no files to read!')
                else:
                    await self.stutter('The files say: ')
                    await self.stutter('\n'.join(self.laptop.files))

            elif task in ['use messenger app', 'messenger app', 'messenger']:
                contacts = ['nasa social media team']
                await self.stutter('In your contacts list are: ')
                for contact in contacts:
                    await self.stutterf(contact)

                await self.stutter('Who would you like to message?')
                invalid_input = True
                while invalid_input:
                    contact = await discord_input(self.discord_client, self.req_channel_name)
                    self.log(contact)
                    if contact in contacts:
                        invalid_input = False
                        if contact in 'nasa social media team':
                            await self.stutter('You can send pictures to NASA to be posted online.')
                            await self.stutter('What picture would you like to send?')
                            picture = await discord_input(self.discord_client, self.req_channel_name)
                            self.log(picture)
                            if 'picture' in picture:
                                if picture in self.player.inventory:
                                    await self.stutter('You send the picture.')
                                    likes = self.player.inventory[picture] * random.randint(10, 1000)
                                    await self.stutter('Your picture gets ' + str(likes) + ' likes.')
                                    del self.player.inventory[picture]
                                else:
                                    await self.stutter("You don't have that picture.")
                            else:
                                await self.stutter("That's not a picture!")
                    else:
                        await self.stutter("They aren't in your contacts list.")

            elif task in 'play text game':
                await ZaryaGame(self.discord_client, self.send_channel, self.req_channel_name).run()

            elif task in 'control station module':
                await self.stutter('A window opens with a few readouts and options.\n'
                                   'periapsis: 390km\n'
                                   'apoapsis: 390km\n'
                                   'inclination: 51.6°\n'
                                   'orbital period: 93 minutes\n'
                                   'thruster statuses: nominal\n'
                                   'alignment: retrograde\n'
                                   "There is a button that says 'fire main engines'.\n"
                                   'Would you like to press it?')
                choice = await discord_input(self.discord_client, self.req_channel_name)
                self.log(choice)
                if 'yes' in choice:
                    await self.stutter('You press the button and tons of Gs force you against the back of the module.\n'
                                       "This is a cargo module, which means there's no seat to help you.\n"
                                       'Your orbit is rapidly falling deeper into the atmosphere.\n'
                                       'The remains of the module hits the ground at terminal velocity.\n'
                                       "But it's ok, because you were already obliterated "
                                       'when its unshielded mass burnt up violently in the atmosphere.\n')
                    await self.stutters('GAME OVER')
                    carry['on'] = False
                    await discord_input(self.discord_client, self.req_channel_name)
                    break
                else:
                    await self.stutter('That was probably a sensible choice.')

            else:
                await self.stutter("The laptop can't do that!")

    # npc interact subroutines
    # async def talktocrewmate():
    #     await self.stutter('Hello there! Glad to see you got that malfunctioning hatch open.')

    # items
    laptop = ZaryaItem(
        name=STRS_ITEMS['laptop']['name'], desc=STRS_ITEMS['laptop']['desc'],
        can_use=True, can_take=False, usefunc=use_laptop
    )
    laptop.state = 'off'
    laptop.tutorial = 'Pending'
    laptop.files = []

    paper = ZaryaItem(
        name=STRS_ITEMS['paper'], desc=STRS_ITEMS['paper']['desc'],
        can_use=True, can_take=True, usefunc=use_paper
    )

    drive = ZaryaItem(
        name=STRS_ITEMS['drive']['name'], desc=STRS_ITEMS['drive']['desc'],
        can_use=True, can_take=True, usefunc=use_drive
    )
    drive.files = {'program.py': "'print('hello world!')'"}

    jumpsuit = ZaryaItem(
        name=STRS_ITEMS['jumpsuit']['name'], desc=STRS_ITEMS['jumpsuit']['desc'],
        can_use=True, can_take=True, usefunc=use_jumpsuit
    )

    greenhouse = ZaryaItem(
        name=STRS_ITEMS['greenhouse']['name'], desc=STRS_ITEMS['greenhouse']['desc'],
        can_use=True, usefunc=use_greenhouse
    )

    camera = ZaryaItem(
        name=STRS_ITEMS['camera']['name'], desc=STRS_ITEMS['camera']['desc'],
        can_use=True, can_take=True, usefunc=use_camera
    )

    toilet = ZaryaItem(
        name=STRS_ITEMS['toilet']['name'], desc=STRS_ITEMS['toilet']['desc'],
        can_use=True, usefunc=use_toilet
    )

    bed = ZaryaItem(
        name=STRS_ITEMS['bed']['name'], desc=STRS_ITEMS['bed']['desc'],
        can_use=True, usefunc=use_bed
    )

    # containers
    zarya_boxes_items = [paper, drive, jumpsuit]
    zarya_boxes = ZaryaContainer(
        name=STRS_GAME['containers']['zarya_boxes']['name'],
        desc=STRS_GAME['containers']['zarya_boxes']['desc'],
        can_leave=True, items=zarya_boxes_items
    )

    # rooms
    zarya = ZaryaRoom(
        name=STRS_ROOMS['zarya']['name'], desc=STRS_ROOMS['zarya']['desc'],
        can_leave=False, items=[laptop], containers=[zarya_boxes]
    )

    unity = ZaryaRoom(
        name=STRS_ROOMS['unity']['name'], desc=STRS_ROOMS['unity']['desc'],
        can_leave=False
    )

    zvezda = ZaryaRoom(
        name=STRS_ROOMS['zvezda']['name'], desc=STRS_ROOMS['zvezda']['desc'],
        can_leave=False, has_windows=True, items=[greenhouse, camera, toilet, bed], ports=zvezda_ports
    )

    # now all rooms are declared, assign cross-references
    zarya.ports = [
        ZaryaPort(name='front', is_open=True, room=unity),
        ZaryaPort('nadir'),
        ZaryaPort(name='aft', is_open=True, room=zvezda),
    ]
    unity.ports = [
        ZaryaPort('front'),
        ZaryaPort('nadir'),
        ZaryaPort('port'),
        ZaryaPort('zenith'),
        ZaryaPort('starboard'),
        ZaryaPort(name='aft', is_open=True, room=zarya),
    ]
    zvezda.ports = [
        ZaryaPort(name='front', is_open=True, room=zarya),
        ZaryaPort('nadir'),
        ZaryaPort('zenith'),
        ZaryaPort('aft'),
    ]

    # player
    player = ZaryaPlayer(
        name=STRS_GAME['player']['name_default'], inventory=[], wearing='jumpsuit'
    )

    # def helpwindow():
    #     helpw = Tk()
    #     helpw.title('help')
    #     helpc = Canvas(helpw, height=(len(help_info)*20)+20, width=650)
    #     helpc.pack()
    #     text = list()
    #     for help_info_item in help_info:
    #         text.append(helpc.create_text(325, (i*20)+20, text=help_info_item))

    skip = False

    current_room = zarya
    previous_room = zarya
    posix_time_ingame = 968716800

    # list of commands for help
    help_info = [
        'help -Shows a list of commands',
        'skip -Toggles stuttering off',
        'noskip -Toggles stuttering on',
        'setname -Changes your name. Legally binding',
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
        'Note:\n You can also use abbreviations for some commands.',
    ]
    # TODO: get this from some module instead?
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    async def run(self):
        await self.stutterf(f'Zarya-Discord v{__version__} \n'
                            '© Joel McBride 2017, 2021 \n'
                            "Remember to report any bugs or errors to 'JMcB#7918' - @ or DM me.")
        await self.n()
        await self.stutter(f"Date: {time.strftime('%d.%m.%Y', time.gmtime(self.posix_time_ingame))}")
        await self.stutter("For a list of commands, type 'help'.")

        # command reader
        carry = {'on': True}
        while carry['on']:
            self.player.sleep += 1
            self.posix_time_ingame += 3600
            await self.n()
            command_input = await discord_input(self.discord_client, self.req_channel_name)
            command_input = command_input.lower()
            self.log(command_input)
            await self.n()

            if command_input in ['help', 'h']:
                help_info_block = '\n'.join(self.help_info)
                await self.stutterf(help_info_block)
                await self.stutter('For the uninitiated: \n'
                                   'In text-based adventure games, a good first command when '
                                   "starting out or \nentering a new place is 'look around'.")

            elif command_input in ['info', 'background', 'b']:
                await self.stutterf(f'Zarya-Discord v{__version__}')
                await self.stutterf('© Joel McBride 2017, 2021')
                await self.stutterf("Remember to report any bugs or errors to 'JMcB#7918' - @ or DM me.")
                await self.stutter('I made this game as one of my first reasonably large projects about four years ago '
                              '(2016). It was very poorly coded but I worked quite a while on it, although after I '
                              "finished most of the framework stuff I couldn't be bothered to add much more content. "
                              "The writing, what there is, is ok, it's got some funny bits I guess. It's also very "
                              'well researched, everything in the game is on the ISS in real life - including Zarya. '
                              'Anyway, I had the idea recently (2021) to make a text based adventure game for Discord, '
                              'so I went back to my old project, touched the code up a bit, ported it, and here we are.')

            # ignore bot-level commands
            elif command_input in ['logs', 'log', 'log.txt']:
                pass

            elif command_input in ['quit', 'q']:
                await self.stutter('Thanks for playing!', self.send_channel)
                break

            elif command_input in ['look around', 'look', 'la', 'l']:
                await self.stutter(f'{self.current_room.desc_stem.rstrip()} {self.current_room.desc}')

                if self.current_room.items:
                    for item in self.current_room.items:
                        await self.stutter(f'{item.desc_stem.rstrip()} {item.desc}')

                if self.current_room.ports:
                    await self.stutter(f'There are {len(self.current_room.ports)} ports: ')
                    for port in self.current_room.ports:
                        port_state = 'open' if port.is_open else 'closed'
                        await self.stutter(f'One to {port.name} that is {port_state}.')

            elif command_input in ['show inventory', 'inventory', 'si', 'i']:
                if not self.player.inventory:
                    await self.stutter('Your inventory is empty.')
                else:
                    await self.stutter('In your inventory is: ')
                    for inventory_item in self.player.inventory:
                        await self.stutter(inventory_item.desc)

            elif command_input.startswith('search'):
                container_to_search = command_input.removeprefix('search').lstrip()
                # could use any() here?
                if container_to_search in [container.name for container in self.current_room.containers]:
                    self.previous_room = self.current_room
                    await self.stutter(f'You search the {container_to_search}.')
                    # TODO: shorten, maybe clean up
                    self.current_room = next([container for container in self.current_room.containers if container.name == container_to_search])

                    if self.current_room.items:
                        await self.stutter(f'The {container_to_search} contain(s):')
                        for item in self.current_room.items:
                            await self.stutter(item.desc)
                    else:
                        await self.stutter("There isn't anything here.")
                else:
                    await self.stutter("That isn't in here.")

            elif command_input in ['leave'] or command_input.startswith(['leave']):
                if self.current_room.can_leave:
                    await self.stutter(f'You leave the {self.current_room.name}.')
                    self.current_room = self.previous_room
                else:
                    await self.stutter(f"I'm sorry {self.player.name}, I'm afraid you can't do that.")

            # TODO: clean this logic statement up
            elif command_input.startswith(('go through', 'gt', 'go')):
                if command_input.endswith('port'):
                    direction = command_input.removesuffix('port').rstrip()
                else:
                    direction = command_input

                # note: less verbose commands must come later in the list or an incomplete prefix could be stripped.
                for prefix in ['go through', 'gt', 'go']:
                    if direction.startswith(prefix):
                        direction = direction.removeprefix(prefix).lstrip()
                        break

                if direction in [port.name for port in self.current_room.ports]:
                    target_port = next([port for port in self.current_room.ports if port.name == direction])
                    if target_port.is_open:
                        await self.stutter(f'You go through the port into {target_port.room.name}.')
                        self.current_room = target_port.room
                    else:
                        await self.stutter('That port is closed.')
                else:
                    await self.stutter("The module you're in doesn't have a port there.")

            elif command_input in ['take all', 'ta']:
                if self.current_room.items:
                    # TODO: ? add ascii art here lol
                    await self.stutter('You: \n'
                                       'TAKE \n'
                                       'ALL THE THINGS.')

                    for item in self.current_room.items:
                        if item.can_take:
                            self.player.inventory.append(item)
                            await self.stutter(f'Youo take the {item.name}.')
                            # TODO: change this? editing in place is discouraged and may not work
                            self.current_room.items.remove(item)
                        else:
                            await self.stutter(f"You can't take the {item.name}.")
                else:
                    await self.stutter("There's nothing here.")

            elif command_input.startswith('take'):
                item_to_take = command_input.removeprefix('take').lstrip()
                if item_to_take in [item.name for item in self.current_room.items]:
                    item = next([item for item in self.current_room.items if item.name == item_to_take])
                    if item.can_take:
                        await self.stutter(f'You take the {item.name}.')
                        self.player.inventory.append(item)
                        self.current_room.items.remove(item)
                    else:
                        await self.stutter("You can't take that.")
                else:
                    await self.stutter("That item isn't here.")

            elif command_input.startswith('use'):
                item_to_use = command_input.removeprefix('use').lstrip()

                # TODO: fix
                if item_to_use in self.player.inventory or item_to_use in self.current_room.items:
                    item = 'uhhh fix this yeah'
                    if item.can_use:
                        await item.usefunc()
                    else:
                        await self.stutter("That item isn't usable.")
                else:
                    await self.stutter("You don't have that item.")

            elif command_input.startswith('drop'):
                item_to_drop = command_input.removeprefix('drop').lstrip()
                if item_to_drop in [item.name for item in self.player.inventory]:
                    item = next([item for item in self.player.inventory if item.name == item_to_drop])
                    await self.stutter(f'You drop the {item.name}.')
                    self.current_room.items.append(item)
                    self.player.inventory.remove(item)
                else:
                    await self.stutter("That item isn't in your inventory.")

            elif command_input in ['skip', 's']:
                self.skip = True
                await self.stutter('Text will now output instantly.')

            elif command_input in ['noskip', 'ns', 'n']:
                self.skip = False
                await self.stutter('Text will now output gradually.')

            # TODO: allow just 'name' as invocation?
            elif command_input.startswith('setname'):
                new_name = command_input.removeprefix('setname').lstrip()
                self.player.name = new_name
                await self.stutter(f"Your name is {self.player.name}.")

            else:
                await self.stutter("That's not a valid command.")

    # logging
    @staticmethod
    def log(text):
        with open('log.txt', 'a+') as log_file:
            log_file.write('\n' + str(text))

    def log_start(self):
        self.log('\n')
        self.log('hello world!')
        self.log(time.strftime('%Y-%m-%d %H:%M:%S'))
