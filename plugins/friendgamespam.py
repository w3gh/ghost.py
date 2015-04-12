import eventlet
from random import SystemRandom
rand = SystemRandom()
from collections import namedtuple

import hook, bnetprotocol
from misc import *
from config import config
friendstalk = hook.import_plugin('friendstalk')

parsed_settings = {}

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
            
        parsed_settings[i]['interval'] = float(settings['interval'])

def spam_loop(bn, d):
    if parsed_settings[bn.id]['ignore']:
        return
        
    while True:
        eventlet.sleep(parsed_settings[bn.id]['interval'])
        gamelist = []
        counter = 0
        for k in friendstalk.friends[friendstalk.bn_to_pool(bn)]:
            v = friendstalk.friends[friendstalk.bn_to_pool(bn)][k]
            if v.general == bnetprotocol.FRIENDLOCATION_PUB:
                    gamelist.append(v.specific)
        if len(gamelist) > 0:
            msg = 'Games: %s' % ', '.join(gamelist)
            bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('/me %s' % msg))
        #DEBUG
        else:
            msg = 'No Games'
            bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('/me %s' % msg))

def install():
    parse_settings()
    hook.register('after-handle_sid_enterchat', spam_loop)

def uninstall():
    hook.unregister('after-handle_sid_enterchat', spam_loop)