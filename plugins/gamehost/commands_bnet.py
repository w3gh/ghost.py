import hook, bnetprotocol
from misc import *
import config

@DebugCall
def on_chatevent(bn, d):
	if d.event == bnetprotocol.EID_WHISPER:
		if str(d.message).split(' ')[0] == config.config['gamehost']['bnet_prefix'] + config.config['gamehost']['bnet_command']:
			bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('/w %s TODO: host game' % (d.user)))

@DebugCall
def install():
	hook.register('after-handle_sid_chatevent', on_chatevent)

@DebugCall
def uninstall():
	hook.unregister('after-handle_sid_chatevent', on_chatevent)
