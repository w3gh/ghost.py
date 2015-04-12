# -*- coding: utf-8 -*- 

import hook
import bnetprotocol
from misc import *
from config import config

settings = config[__name__.split('.')[-1]]

def message_received(bn, d):
	if d.event == bnetprotocol.EID_TALK:
		if str(d.message).split(' ')[0] == settings['trigger'] + 'slapme':
			bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('/me ударил %s' % (d.user)))

def install():
	hook.register('after-handle_sid_chatevent', message_received)

def uninstall():
	hook.unregister('after-handle_sid_chatevent', message_received)
