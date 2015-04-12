import eventlet
from random import SystemRandom
rand = SystemRandom()

import hook, bnetprotocol
from misc import *
from config import config
clantrack = hook.import_plugin('clantrack')

invitations = {}

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
            
        parsed_settings[i]['minrank'] = int(settings['minrank'])
        parsed_settings[i]['command'] = settings['command']
        parsed_settings[i]['clantrack_pool'] = settings['clantrack_pool']

def message_received(bn, d):
    if d.event == bnetprotocol.EID_TALK:
        msg_list = str(d.message).split(' ', 1)
        try:
            command, payload = msg_list
        except ValueError:
            command = msg_list[0]
            payload = ''
        if command == parsed_settings[bn.id]['command'] and len(payload) > 0 \
            and clantrack.get_clanmember_rank(bn, str(d.user)) >= int(parsed_settings[bn.id]['minrank']):
            cookie = rand.randint(0, 2147483647)
            invitations[cookie] = payload
            bn.send_packet(bnetprotocol.SEND_SID_CLANINVITATION(cookie, payload))

def claninvitation_feedback(bn, d):
    message = ''
    if d.result == 0:
        message = '%s is now in %s.' % (str(invitations[d.cookie]), clantrack.clantags[bn.id])
    elif d.result == 4:
        message = '%s refused the invitation to %s.' % (str(invitations[d.cookie]), clantrack.clantags[bn.id])
    elif d.result == 5:
        message = 'An error occured while inviting %s to %s.' % (str(invitations[d.cookie]), clantrack.clantags[bn.id])
    elif d.result == 9:
        message = '%s could not join %s because it is full.' % (str(invitations[d.cookie]), clantrack.clantags[bn.id])
    
    del invitations[d.cookie]
    
    bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND(message))

@DebugCall
def install():
    parse_settings()
    hook.register('after-handle_sid_chatevent', message_received)
    hook.register('after-handle_sid_claninvitation', claninvitation_feedback)

@DebugCall
def uninstall():
    hook.unregister('after-handle_sid_chatevent', message_received)
    hook.unregister('after-handle_sid_claninvitation', claninvitation_feedback)