# -*- coding: utf-8 -*- 

import hook
import bnetprotocol
from misc import *
from config import config

#settings = config[__name__.split('.')[-1]]

def message_received(bn, d):
	if d.event == bnetprotocol.EID_TALK:
		msg_list = str(d.message).split(' ', 1)
		try:
			command, payload = msg_list
		except ValueError:
			command = msg_list[0]
			payload = ''
		if command == '.join' and len(payload) > 0:
			'''if str(d.message).split(' ')[0] == settings['trigger'] + 'join':'''
			bn.send_packet(bnetprotocol.SEND_SID_CHATCOMMAND('/join %s' % (payload)))
def install():
	hook.register('after-handle_sid_chatevent', message_received)

def uninstall():
	hook.unregister('after-handle_sid_chatevent', message_received)
