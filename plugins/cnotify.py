import eventlet

import hook, bnetprotocol
from misc import *
from config import config
clantrack = hook.import_plugin('clantrack')

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

spam_locks = {}

def message_received(bn, d):
    if parsed_settings[bn.id]['ignore']:
        return
        
    if d.event == bnetprotocol.EID_TALK:
        msg_list = str(d.message).split(' ', 1)
        try:
            command, payload = msg_list
        except ValueError:
            command = msg_list[0]
            payload = ''
        if command == parsed_settings[bn.id]['command'] and len(payload) > 0 \
           and clantrack.get_clanmember_rank(bn, str(d.user)) >= int(parsed_settings[bn.id]['minrank']):
            onlinenames = clantrack.get_online_clanmembers(bn)
            pool = clantrack.bn_to_pool(bn)
            if spam_locks.get(pool, False) == False:
                spam_locks[pool] = True
                bn_pool = clantrack.list_of_bnet_objects(pool)
                bn_count = len(bn_pool)
                bn_i = 0
                current_bn = bn_pool[0]
                current_bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('Adding %d to Clan Notify List' % len(onlinenames)))

                for i in onlinenames:
                    current_bn, bn_i = next_in_circular_list(bn_pool, bn_i)
                    current_bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('/w %s %s' % (i, payload)))
                    atomic_debug('whispering to %s using %s' % (i, repr(current_bn)))
                    eventlet.sleep(3./bn_count)
                    
                current_bn, bn_i = next_in_circular_list(bn_pool, bn_i)
                current_bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND(', '.join(clantrack.clantags_in_pool(pool)) + ' Done sending messages.'))
                spam_locks[pool] = False
            else:
                atomic_debug('pool %d is spamlocked' % pool)

def install():
    parse_settings()
    hook.register('after-handle_sid_chatevent', message_received)

def uninstall():
    hook.unregister('after-handle_sid_chatevent', message_received)