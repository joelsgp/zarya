import os
import json
import time
import random

from typing import List, Callable
# from tkinter import *

import aiohttp

from .discord_funcs import discord_stutter, discord_input


# idea: dungeon crawler mode? https://discord.com/channels/714154158969716780/736664393630220289/805862557033299992
# could make some bizarre plotline for it, aliens probably
# todo: make more things in the strings file
# todo: https://discord.com/channels/714154158969716780/736664393630220289/805872416521846795
# todo: aliases for items
# todo: `inspect` command
# todo: help command with argument


__version__ = '0.11.0'


DISCORD_NAME = 'JMcB#7918'
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

    def __str__(self):
        return self.name


class Picture(ZaryaItem):
    """Subclass to distinguish pictures from other items."""
    def __init__(self, quality: int = None):
        if quality is None:
            quality = random.randint(1, 10)
        self.quality = quality

        if self.quality <= 2:
            self.picture_adj = 'rubbish'
        elif self.quality <= 5:
            self.picture_adj = 'nice'
        else:
            self.picture_adj = 'beautiful'

        super().__init__(name=f'{self.picture_adj} picture', desc=f'a {self.picture_adj} picture', can_take=True)


class Laptop(ZaryaItem):
    """Subclass for the laptop item, with additional attributes."""
    powered_on = False
    tutorial_done = False
    files = {}


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

    def __init__(
            self, name: str, desc: str, can_leave: bool = True, has_windows: bool = False,
            items: List[ZaryaItem] = None
    ):
        self.name = name
        if desc.startswith(self.desc_stem):
            desc = desc.removeprefix(self.desc_stem)
        self.desc = desc.strip()
        self.can_leave = can_leave
        self.has_windows = has_windows
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
        super().__init__(name, desc, can_leave, has_windows, items)

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
        sleepiness -- how much sleep as a float
    """
    name = STRS_GAME['player']['name_default']

    def __init__(self, name: str, inventory: List[ZaryaItem], wearing, sleepiness: float = 5):
        self.name = name
        self.inventory = inventory
        self.wearing = wearing
        self.sleepiness = sleepiness

    def __str__(self):
        return self.name

    async def sleep(self, game_instance):
        """Sleep for a period of time determined by the sleepiness attribute."""
        if self.sleepiness > 8:
            await game_instance.stutter('You sleep until you are no longer tired.')
            game_instance.posix_time_ingame += self.sleepiness * 3600
            self.sleepiness = random.randint(0, 2)
            await game_instance.stutter(
                f"Date: {time.strftime('%d.%m.%Y', time.gmtime(game_instance.posix_time_ingame))}"
            )
        else:
            await game_instance.stutter('You are not tired enough to get to sleep.')


class ZaryaGame:
    def __init__(self, discord_client, send_channel, req_channel_name=None):
        self.discord_client = discord_client
        self.send_channel = send_channel
        if req_channel_name is None:
            self.req_channel_name = ''
        else:
            self.req_channel_name = req_channel_name

        self.carry = {'on': True}
        self.skip = False
        # 12 sep 2000
        self.posix_time_ingame = 968716800

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
        # note: what was this meant to be used for?
        await self.stutter('The strip of paper has a password on it. \n'
                           "'Pa$$word123' \n"
                           'You wonder what it is the password to. \n'
                           "(That's your cue to wonder what it is the password to)")

    async def use_drive(self):
        for itemspace in self.player.inventory, self.current_room.items:
            laptop_in_itemspace = [i for i in itemspace if isinstance(i, Laptop)]
            if laptop_in_itemspace:
                laptop = laptop_in_itemspace[0]
                if self.drive.files:
                    await self.stutter('You transfer all the files on the usb stick to the laptop.')
                    laptop.files = self.drive.files
                    self.drive.files = {}
                else:
                    await self.stutter('There are no files on the usb stick.')
                break
        else:
            await self.stutter('You have no laptop to use it with.')

    async def use_jumpsuit(self):
        await self.stutter('You put on the jumpsuit.')
        self.player.wearing = 'Russian jumpsuit'
        await self.stutter('You were already wearing one, however, so you are now wearing two jumpsuits.')
        await self.stutter('Good job.')

    async def use_greenhouse(self):
        await self.stutter('You watch the sprouts.')
        await self.stutters('Nothing interesting happens.')

    async def use_camera(self):
        # TODO; more detailed pictures e.g. what the picture is of?
        if self.current_room.has_windows:
            new_picture = Picture()
            await self.stutterl('You take the camera to a window and, after fiddling with '
                                'lenses and settings for\na few minutes, take a ')
            await self.stutter(f'{new_picture.name}.')

            self.player.inventory.append(new_picture)
        else:
            await self.stutter('There are no windows to take pictures out of in this module.')

    async def use_toilet(self):
        await self.stutter("You do your business in the space toilet. Don't ask an astronaut "
                           "how this \nhappens if you meet one, they're tired of the question.")

    async def use_bed(self):
        await self.stutter("You get in the 'bed'.")
        await self.player.sleep(self)
        await self.stutter('You get back out of the bed.')

    async def use_laptop(self):
        # tutorial
        if not self.laptop.tutorial_done:
            await self.stutter('There is a sticker on the laptop that lists things you can do with it:')
            await self.stutterf('browse web \n'
                                'use messenger app \n'
                                'read files \n'
                                'play text game \n'
                                'control station module')
            await self.stutter("Now that you've read the sticker, you peel it off.")
            self.laptop.tutorial_done = True
            await self.n()

        await self.stutter('You turn on the laptop.')
        self.laptop.powered_on = True
        while self.laptop.powered_on:
            await self.n()
            task = await discord_input(self.discord_client, self.req_channel_name)
            self.log(task)
            await self.n()

            if task in ('turn off laptop', 'turn off', 'off', 'close laptop', 'close', 'quit'):
                await self.stutter('You turn off the laptop.')
                self.laptop.powered_on = False

            elif task in ['h', 'help', 'tutorial', 'redo tutorial', 'sticker', 'put sticker back on']:
                self.laptop.tutorial_done = False
                await self.stutter(
                    'You decide to stick the sticker that lists what you can do with the laptop '
                    'back on. \n'
                    'If you want to read it again, you have to turn the laptop off and on again. \n'
                    'You think this is pretty stupid.'
                )

            # todo: puzzle for connecting to the internet?
            elif task in ['browse the web', 'browse web', 'browse', 'web', 'browser', 'web browser']:
                await self.stutter('A browser window opens. Where do you want to go?')
                url = await discord_input(self.discord_client, self.req_channel_name)
                self.log(url)
                try:
                    if not url.startswith('http'):
                        url = 'http://' + url
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as response:
                            html = await response.text()
                    await self.stutter(html, skip=True)
                    await self.stutter("Hmm, looks like there's no GUI. \n"
                                       'Oh well.')
                except ValueError:
                    await self.stutter("That's not a valid URL.")
                except aiohttp.ClientConnectorError:
                    await self.stutter("The site had an error.")

            elif task in ['read files', 'read', 'files']:
                if not self.laptop.files:
                    await self.stutter('You have no files to read!')
                else:
                    await self.stutter('The files say: ')
                    await self.stutter('\n'.join([f'{key}: {value}' for key, value in self.laptop.files.items()]))

            elif task in ['use messenger app', 'messenger app', 'messenger']:
                contacts = ['nasa social media team']
                await self.stutter('In your contacts list are: ')
                for contact in contacts:
                    await self.stutterf(contact)

                await self.stutter('Who would you like to message?')
                contact = await discord_input(self.discord_client, self.req_channel_name)
                self.log(contact)
                if contact in contacts:
                    if contact in 'nasa social media team':
                        pictures_in_inv = [p for p in self.player.inventory if isinstance(p, Picture)]
                        pictures_list = ' \n'.join([p.name for p in pictures_in_inv])

                        await self.stutter('You can send pictures to NASA to be posted online. \n'
                                           'What picture would you like to send? \n'
                                           f"{pictures_list}")
                        picture_to_send = await discord_input(self.discord_client, self.req_channel_name)
                        self.log(picture_to_send)

                        if 'picture' in picture_to_send:
                            if picture_to_send in [p.name for p in pictures_in_inv]:
                                await self.stutter('You send the picture.')
                                picture = [p for p in pictures_in_inv if p.name == picture_to_send][0]
                                likes = (picture.quality ** 2) * random.randint(10, 1000)
                                await self.stutter(f'Your picture gets {likes} likes.')
                                await self.stutter('You delete the picture to free up valuable storage space.')
                                self.player.inventory.remove(picture)
                            else:
                                await self.stutter("You don't have that picture.")
                        else:
                            await self.stutter("That's not a picture!")
                else:
                    await self.stutter("They aren't in your contacts list.")

            # todo: fix moving between rooms, again
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
                                   'Would you like to press it? (yes/no)')
                choice = await discord_input(self.discord_client, self.req_channel_name)
                self.log(choice)
                if choice == 'yes':
                    await self.stutter('A dialog box pops up: ARE YOU SURE? (yes/no)')
                    choice_confirm = await discord_input(self.discord_client, self.req_channel_name)
                    self.log(choice_confirm)
                    if choice_confirm == 'yes':
                        await self.stutter('You press the button and tons of Gs force you against the back of the '
                                           'module. \n'
                                           "This is a cargo module, which means there's no seat to help you. \n"
                                           'Your orbit is rapidly falling deeper into the atmosphere. \n'
                                           'The remains of the module hits the ground at terminal velocity. \n'
                                           "But it's ok, because you were already obliterated "
                                           'when its unshielded mass burnt up violently in the atmosphere.\n')
                        await self.stutters('GAME OVER')
                        self.carry['on'] = False
                        break
                    else:
                        await self.stutter('You chicken out. Chicken. (chicken go cluck cluck)')
                else:
                    await self.stutter('That was probably a sensible choice.')

            else:
                await self.stutter("The laptop can't do that!")

    # npc interact subroutines
    # async def talktocrewmate():
    #     await self.stutter('Hello there! Glad to see you got that malfunctioning hatch open.')

    # items
    laptop = Laptop(
        name=STRS_ITEMS['laptop']['name'], desc=STRS_ITEMS['laptop']['desc'],
        can_use=True, can_take=True, usefunc=use_laptop
    )

    paper = ZaryaItem(
        name=STRS_ITEMS['paper']['name'], desc=STRS_ITEMS['paper']['desc'],
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
        can_leave=False, has_windows=True, items=[greenhouse, camera, toilet, bed]
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
        name=STRS_GAME['player']['name_default'].title(), inventory=[], wearing='jumpsuit'
    )

    # def helpwindow():
    #     helpw = Tk()
    #     helpw.title('help')
    #     helpc = Canvas(helpw, height=(len(help_info)*20)+20, width=650)
    #     helpc.pack()
    #     text = list()
    #     for help_info_item in help_info:
    #         text.append(helpc.create_text(325, (i*20)+20, text=help_info_item))

    current_room = zarya
    previous_room = zarya

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
    months = (
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    )

    async def process_command(self, command_input):
        if command_input in ['help', 'h', 'commands']:
            help_info_block = '\n'.join(self.help_info)
            await self.stutterf(help_info_block)
            await self.stutter('For the uninitiated: \n'
                               'In text-based adventure games, a good first command when '
                               "starting out or \nentering a new place is 'look around'.")

        elif command_input in ['info', 'background', 'b']:
            await self.stutterf(
                f'Zarya-Discord v{__version__} \n'
                '© Joel McBride 2017, 2021 \n'
                "Remember to report any bugs or errors to 'JMcB#7918' - @ or DM me."
            )
            await self.stutter(
                'I made this game as one of my first reasonably large projects about four years ago '
                '(2016). It was very poorly coded but I worked quite a while on it, although after I '
                "finished most of the framework stuff I couldn't be bothered to add much more content. "
                "The writing, what there is, is ok, it's got some funny bits I guess. It's also very "
                'well researched, everything in the game is on the ISS in real life - including Zarya. '
                'Anyway, I had the idea recently (2021) to make a text based adventure game for Discord, '
                'so I went back to my old project, touched the code up a bit, ported it, and here we are.'
            )

        # ignore bot-level commands
        elif command_input in ['logs', 'log', 'log.txt']:
            pass

        elif command_input in ['quit', 'q']:
            self.carry['on'] = False

        elif command_input in ['look around', 'look', 'la', 'l']:
            # todo: more detailed info on windows
            # todo: tell user where the ports lead?
            await self.stutter(f'{self.current_room.desc_stem.rstrip()} {self.current_room.desc}.')
            if self.current_room.has_windows:
                await self.stutter('There are windows.')

            if self.current_room.items:
                item_descs = [f'{i.desc_stem.rstrip()} {i.desc}.' for i in self.current_room.items]
                await self.stutter(' \n'.join(item_descs))

            # only check for ports if room (not container)
            if isinstance(self.current_room, ZaryaRoom):
                if self.current_room.ports:
                    ports_list = f'There are {len(self.current_room.ports)} ports:'
                    for port in self.current_room.ports:
                        port_state = 'open' if port.is_open else 'closed'
                        ports_list += f' \nOne to {port.name} that is {port_state}.'

                    await self.stutter(ports_list)

        elif command_input in ['show inventory', 'inventory', 'si', 'i']:
            if not self.player.inventory:
                await self.stutter('Your inventory is empty.')
            else:
                await self.stutter('In your inventory is: ')
                for inventory_item in self.player.inventory:
                    await self.stutter(inventory_item.name)

        elif command_input == 'buyburger':
            await self.stutter('BURGER. 🍔 MMM...')

        elif command_input.startswith('search'):
            container_to_search = command_input.removeprefix('search').lstrip()
            # could use any() here?
            if container_to_search in [container.name for container in self.current_room.containers]:
                self.previous_room = self.current_room
                await self.stutter(f'You search the {container_to_search}.')
                # todo: make this kind of functionality a method of the room and the player's inventory.
                self.current_room = [c for c in self.current_room.containers if c.name == container_to_search][0]

                if self.current_room.items:
                    items_list = f'The {container_to_search} contain(s): \n'
                    items_list += ' \n'.join([i.desc for i in self.current_room.items])
                    await self.stutter(items_list)
                else:
                    await self.stutter("There aren't any items in here.")
            else:
                await self.stutter("That isn't in here.")

        elif command_input in ('leave',) or command_input.startswith(('leave',)):
            if self.current_room.can_leave:
                await self.stutter(f'You leave the {self.current_room.name}.')
                self.current_room = self.previous_room
            else:
                await self.stutter(f"I'm sorry {self.player.name}, I'm afraid you can't do that.")

        elif command_input.startswith(('go through', 'gt', 'go')):
            if isinstance(self.current_room, ZaryaContainer) and not isinstance(self.current_room, ZaryaRoom):
                await self.stutter("You're searching a container, use 'leave' to leave.")
                return

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
                target_port = [p for p in self.current_room.ports if p.name == direction][0]
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

                items_to_remove = []
                for item in self.current_room.items:
                    if item.can_take:
                        self.player.inventory.append(item)
                        await self.stutter(f'You take the {item.name}.')
                        items_to_remove.append(item)
                    else:
                        await self.stutter(f"You can't take the {item.name}.")
                for item in items_to_remove:
                    self.current_room.items.remove(item)
            else:
                await self.stutter("There's nothing here.")

        elif command_input.startswith(('take', 'pick up')):
            for prefix in ('take', 'pick up'):
                if command_input.startswith(prefix):
                    item_to_take = command_input.removeprefix(prefix).lstrip()

                    if item_to_take in [i.name for i in self.current_room.items]:
                        item = [i for i in self.current_room.items if i.name == item_to_take][0]
                        if item.can_take:
                            await self.stutter(f'You take the {item.name}.')
                            self.player.inventory.append(item)
                            self.current_room.items.remove(item)
                        else:
                            await self.stutter("You can't take that.")
                    else:
                        await self.stutter("That item isn't here.")
                    break

        elif command_input.startswith('use'):
            item_to_use = command_input.removeprefix('use').lstrip()

            # TODO: reduce duplicated code (the bit with a listcomp)
            for itemspace in (self.player.inventory, self.current_room.items):
                if item_to_use in [i.name for i in itemspace]:
                    item = [i for i in itemspace if i.name == item_to_use][0]
                    if item.can_use:
                        await item.usefunc(self)
                    else:
                        await self.stutter("That item isn't usable.")
                    break
            else:
                await self.stutter("You don't have that item.")

        elif command_input.startswith('drop'):
            item_to_drop = command_input.removeprefix('drop').lstrip()
            if item_to_drop in [item.name for item in self.player.inventory]:
                item = [i for i in self.player.inventory if i.name == item_to_drop][0]
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

        elif command_input.startswith(('name', 'setname', 'my name is')):
            for command_invoc in ('name', 'setname', 'my name is'):
                if command_input.startswith(command_invoc):
                    new_name = command_input.removeprefix(command_invoc).lstrip()
                    self.player.name = new_name
                    await self.stutter(f'Your name is {self.player.name}.')

        else:
            await self.stutter("That's not a valid command.")

    async def run(self):
        await self.stutterf(
            f'Zarya-Discord v{__version__} \n'
            '© Joel McBride 2017, 2021 \n'
            f"Remember to report any bugs or errors to '{DISCORD_NAME}' - @ or DM me. \n"
        )
        await self.n()
        await self.stutter(
            f"Date: {time.strftime('%d.%m.%Y', time.gmtime(self.posix_time_ingame))} \n"
            "For a list of commands, type 'help'."
        )

        while self.carry['on']:
            self.player.sleepiness += 1
            # one hour
            self.posix_time_ingame += 60 ** 3
            # could check at like 8 as well but don't want to bother the player, it's not an educational game
            if self.player.sleepiness == 24:
                await self.stutter("You haven't slept for a while. You're starting to feel very sleepy.")
            elif self.player.sleepiness == 40:
                await self.stutter("You haven't slept in too long. "
                                   "You're very, very tired and you're going to black out soon.")
            elif self.player.sleepiness == 48:
                await self.stutter("You start to nod off. Before you fall asleep you realise you haven't slept in "
                                   'about two days.')
                await self.player.sleep(self)
                await self.stutter('You wake up floating around. You should have slept in your bed sooner.')

            await self.n()
            command_input = await discord_input(self.discord_client, self.req_channel_name)
            command_input = command_input.lower()
            self.log(command_input)
            await self.n()
            await self.process_command(command_input)

        await self.stutter('Thanks for playing!')

    # logging
    @staticmethod
    def log(text):
        with open('log.txt', 'a+') as log_file:
            log_file.write('\n' + str(text))

    def log_start(self):
        self.log('\n')
        self.log('hello world!')
        self.log(time.strftime('%Y-%m-%d %H:%M:%S'))
