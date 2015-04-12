import nativethread
import time
import eventlet
import sys

def slowass_function(x):
	time.sleep(3)
	return x

def atomic_print(x):
	sys.stdout.write(x + '\r\n')

def spammer(x):
	while True:
		atomic_print(x)
		eventlet.sleep(0.2)

def slow_print(x):
	atomic_print(nativethread.execute(slowass_function, x))

eventlet.spawn_n(spammer, 'bleh')
eventlet.spawn_n(spammer, 'hurf')
eventlet.spawn_n(spammer, 'durf')
eventlet.spawn_n(spammer, 'blurf')
pool = eventlet.GreenPool()
pool.spawn_n(slow_print, 'wtf')
pool.waitall()
