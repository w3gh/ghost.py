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

@DebugCall
def message_received(bn, d):
    if parsed_settings[bn.id]['ignore']:
        return
        
    if d.event == bnetprotocol.EID_TALK:
        if str(d.message).split(' ')[0] == parsed_settings[bn.id]['command'] \
          and clantrack.get_clanmember_rank(bn, str(d.user)) >= int(parsed_settings[bn.id]['minrank']):
            onlinenames = clantrack.get_online_clanmembers(bn)
            liststring = ', '.join(onlinenames)
            message = ', '.join(clantrack.clantags_in_pool(clantrack.bn_to_pool(bn))) + ' (' + str(len(onlinenames)) + '): ' + liststring
            bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND(message))

def install():
    parse_settings()
    hook.register('after-handle_sid_chatevent', message_received)

def uninstall():
    hook.unregister('after-handle_sid_chatevent', message_received)