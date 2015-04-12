# Extremely basic. Flags as in <game> when whisper is received.
# Flags as in channel when we see them join our channel (doesn't record channel name either)
# Does not detect offline/online or anything else.

import eventlet
from random import SystemRandom
rand = SystemRandom()
from collections import namedtuple
import re

import hook, bnetprotocol
from misc import *
from config import config

friends = {}
bn_ids = {} # keyed by pool

parsed_settings = {}

FriendLocation = namedtuple('FriendLocation', ('general', 'specific'))

def parse_settings():
    for i in xrange(9001):
        try:
            settings = config[__name__.split('.')[-1] + str(i)]
        except KeyError:
            break
        parsed_settings[i] = {}
        
        ignore = int(settings.get('ignore', '0'))
        parsed_settings[i]['ignore'] = ignore
        if ignore:
            continue
        
        
        parsed_settings[i]['pool'] = int(settings['pool'])
        friends[parsed_settings[i]['pool']] = {}
        bn_ids[parsed_settings[i]['pool']] = i
        
def bn_to_pool(bn):
    return parsed_settings[bn.id]['pool']
        
def message_received(bn, d):
    if parsed_settings[bn.id]['ignore']:
        return
        
    if d.event == bnetprotocol.EID_WHISPER:
        desired_prefix = 'Your friend %s entered a Warcraft III The Frozen Throne game called ' % d.user
        if d.message.startswith(desired_prefix):
            gamename = d.message[len(desired_prefix):-1]
            #bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('DEBUG: "%s" has joined "%s"' % (d.user, gamename)))
            friends[bn_to_pool(bn)][str(d.user)] = FriendLocation(bnetprotocol.FRIENDLOCATION_PUB, str(gamename))
    elif d.event == bnetprotocol.EID_JOIN:
        if friends[bn_to_pool(bn)].get(str(d.user), None) is not None:
            friends[bn_to_pool(bn)][str(d.user)] = FriendLocation(bnetprotocol.FRIENDLOCATION_CHAT, '')
    elif d.event == bnetprotocol.EID_INFO:
        no_full_stop = str(d.message[:-1])
        mo = re.match('[0-9]*: ([A-Za-z.0-9]*), \(mutual\) using Warcraft III The Frozen Throne in the (game|channel) (.*)', no_full_stop)
        if mo is not None:
            # bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('DEBUG: "%s" in "%s" "%s"' %
                # (mo.group(1), mo.group(2), mo.group(3))))
            general_loc = mo.group(2)
            if general_loc == 'game':
                friends[bn_to_pool(bn)][mo.group(1)] = FriendLocation(bnetprotocol.FRIENDLOCATION_PUB, mo.group(3))
            elif general_loc == 'channel':
                friends[bn_to_pool(bn)][mo.group(1)] = FriendLocation(bnetprotocol.FRIENDLOCATION_CHAT, mo.group(3))
        
def send_fl(bn, d):
    bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('/f l'))
        
def install():
    parse_settings()
    hook.register('after-handle_sid_chatevent', message_received)
    hook.register('after-handle_sid_enterchat', send_fl)

def uninstall():
    hook.unregister('after-handle_sid_chatevent', message_received)
    hook.unregister('after-handle_sid_enterchat', send_fl)