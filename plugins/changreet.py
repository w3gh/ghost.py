import hook, bnetprotocol
from misc import *
from config import config

parsed_settings = None

def parse_settings():
    global parsed_settings
    parsed_settings = {}
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
            
        parsed_settings[i]['admins'] = settings['admins'].lower().split(',')
        parsed_settings[i]['msg'] = settings['msg']
        parsed_settings[i]['command'] = settings['command']
            
            
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
        if command == parsed_settings[bn.id]['command'] and str(d.user).lower() in parsed_settings[bn.id]['admins']:
            parsed_settings[bn.id]['msg'] = payload
            bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND(b'Greeting changed.'))
            
    elif d.event == bnetprotocol.EID_JOIN:
        bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND(b'/w ' + d.user + ' ' + parsed_settings[bn.id]['msg']))
    
def install():
    parse_settings()
    hook.register('after-handle_sid_chatevent', message_received)
    
def uninstall():
    hook.unregister('after-handle_sid_chatevent', message_received)