from ConfigParser import RawConfigParser
import io

# Global
config = {}

def load(config_files):
    global config
    config = {}
    cp = RawConfigParser()
    cp.read(config_files)
    
    for section in cp.sections():
        if config.get(section, None) == None:
            config[section] = {}
        for option in cp.options(section):
            config[section][option] = cp.get(section, option) #.strip()