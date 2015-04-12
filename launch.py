#!/usr/bin/env python

import os

import config

core_module = None # to facilitate backdoor

def main(argv): # argv should be a list of config files, parsed in that order
    config_files = argv[1:] # chop off actual program
    
    if len(config_files) < 1:
        config_files.append('default.cfg')
    if len(config_files) < 2: 
        config_files.append('gghost.cfg')
    config.load(config_files)
    
    # Set up the environment
    os.environ.update(config.config['environ'])
    
    # Get eventlet loaded, so hook.py can detect it
    
    import eventlet
    from eventlet import backdoor
    
    # Initialise backdoor
    if int(config.config['launch'].get('backdoor', '1')):
        eventlet.spawn(backdoor.backdoor_server,
                       eventlet.listen((config.config['launch'].get('backdoor_bind', '127.0.0.1'),
                       int(config.config['launch'].get('backdoor_port', '3000')))))
    
    
    # Initialise plugins
    import hook
    for plugin in config.config['launch']['plugins'].split(','):
        hook.install(plugin)
    
    # Let's run
    core_module = __import__(config.config['launch']['core'])
    eventlet.spawn(core_module.launch).wait()
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
