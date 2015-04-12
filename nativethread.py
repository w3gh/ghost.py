import threading
import collections
import Queue
import os
import time
import sys

_green_sleep = None
if 'gevent' in sys.modules.keys():
	import gevent
	_green_sleep = gevent.sleep
elif 'eventlet' in sys.modules.keys():
	import eventlet
	_green_sleep = eventlet.sleep

_totalthreadcount = 0
_threadpool = collections.deque()
_entirethreadpool = collections.deque()
_threadcount = 0
_threadcountlock = threading.Lock()
_jobqueue = Queue.Queue(maxsize=-1)
_reservedthreads = collections.deque()

class ActualPoolThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True

	def run(self):
		global _threadpool, _threadcount, _threadcountlock, _jobqueue
		while True:
			with _threadcountlock: # Indicate that we're idle
				_threadcount += 1
				_threadpool.append(self)
			
			resq, meth, args, kwargs = _jobqueue.get()
			
			with _threadcountlock: # Indicate that we're busy
				_threadcount -= 1
				_threadpool.remove(self)

			resq.put(meth(*args, **kwargs))
			#_jobqueue.task_done() # not needed since we're not join()ing

def new_thread():
	global _totalthreadcount, _entirethreadpool
	_totalthreadcount += 1
	t = ActualPoolThread()
	_entirethreadpool.append(t)
	t.start()

def execute(meth, *args, **kwargs):
	#return meth(*args, **kwargs) # dummy. comment out for production use
	global _totalthreadcount, _threadpool, _entirethreadpool, _threadcount, _threadcountlock, _jobqueue
	
	if threading.currentThread() in _entirethreadpool:
		return meth(*args, **kwargs)
	
	resq = Queue.Queue(1)
	_jobqueue.put((resq, meth, args, kwargs))
	
	if _threadcount == 0 and _totalthreadcount < int(os.environ.get('NATIVETHREAD_POOL_SIZE', '20')):
		new_thread()
	
	res = None
	while True:
		try:
			time.sleep(0)
			res = resq.get_nowait()
			break
		except Queue.Empty:
			try:
				_green_sleep()
			except:
				pass
	return res

class ActualReservedThread(threading.Thread):
	def __init__(self, jobq):
		threading.Thread.__init__(self)
		self.daemon = True
		self.jobq = jobq
	def run(self):
		while True:
			resq, meth, args, kwargs = self.jobq.get()
			resq.put(meth(*args, **kwargs))

class ReservedThread:
	def __init__(self):
		self.jobq = Queue.Queue(maxsize=-1)
		self.actualThread = ActualReservedThread(self.jobq)
		self.actualThread.start()

	def execute(self, meth, *args, **kwargs):
		#return meth(*args, **kwargs) # dummy. comment out for production use
		if threading.currentThread() is self.actualThread:
			return meth(*args, **kwargs)
		resq = Queue.Queue(1)
		self.jobq.put((resq, meth, args, kwargs))

		res = None
		while True:
			try:
				time.sleep(0)
				res = resq.get_nowait()
				break
			except Queue.Empty:
				try:
					_green_sleep()
				except:
					pass
		return res

class DummyThread:
	def execute(self, meth, *args, **kwargs):
		return meth(*args, **kwargs)

