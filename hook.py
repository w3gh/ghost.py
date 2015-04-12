import imp
import sys
from misc import *

_GreenPool = None
_spawn_raw = None
# if 'gevent' in sys.modules.keys():
    # import gevent, gevent.pool
    # _GreenPool = gevent.pool.Pool
    # _spawn_raw = gevent.spawn_raw
    # gevent.Greenlet.wait = lambda self: self.get(True)
# elif 'eventlet' in sys.modules.keys():
import eventlet
_GreenPool = eventlet.GreenPool
_GreenPool.spawn_raw = _GreenPool.spawn_n
_GreenPool.join = _GreenPool.waitall
_spawn_raw = eventlet.spawn_n
# else:
    # raise RuntimeError('Engine not loaded.')

_hooks = {}
_modules = {}

def _create_hook(name): # internal shit just to make sure the crap is initialised
    if not _hooks.get(name, None):
        _hooks[name] = []

def import_plugin(modname): # convenience function for plugins that depend on other plugins
    if _modules.get(modname, None) is None:
        f, p, d = imp.find_module(modname, ['plugins'])
        _modules[modname] = imp.load_module('plugins.' + modname, f, p, d)
    return _modules[modname]
    
def unref_plugin(modname): # removes references to a plugin
    del _modules[modname]

def register(name, fn): # register a hook (called by plugin)
    _create_hook(name)
    if not fn in _hooks[name]:
        _hooks[name].append(fn)

def unregister(name, fn): # unregister a hook (called by plugin)
    _create_hook(name)
    if fn in _hooks[name]:
        _hooks[name].remove(fn)	

def install(modname): # install a module
    import_plugin(modname).install()

def uninstall(modname): # uninstall a module
    import_plugin(modname).uninstall()

def call_wait(name, *args, **kwargs): # call all hooks registered under "name" and wait for results
    _create_hook(name)
    gp = _GreenPool()
    greenlets = [ gp.spawn(i, *args, **kwargs) for i in _hooks[name] ]
    gp.join()
    results = [ i.wait() for i in greenlets ] # a list of return values. probably True or False to tell
                                              # caller to abandon it's own processor (a la JavaScript)
    return results

def call_nowait(name, *args, **kwargs): # call all hooks registered under "name" and return immediately
    _create_hook(name)
    for i in _hooks[name]:
        _spawn_raw(i, *args, **kwargs)
