import sys

def atomic_print(x):
	sys.stdout.write(x + '\r\n')

def atomic_debug(x):
	sys.stderr.write(x + '\r\n')

def next_in_circular_list(list, index):
    index += 1
    current = None
    try:
        current = list[index]
    except IndexError:
        index = 0
        current = list[index]
    return (current, index)
    
class DebugCall:
	def __init__(self, fn):
		self.fn = fn
	def __call__(self, *args, **kwargs):
		atomic_debug('In %s' % self.fn.__name__)
		ret = self.fn(*args, **kwargs)
		atomic_debug('Finished %s' % self.fn.__name__)
		return ret
