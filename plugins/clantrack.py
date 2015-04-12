from random import SystemRandom
rand = SystemRandom()

import hook, bnetprotocol, bnet
from misc import *
from config import config

parsed_settings = {}
bn_ids = {} # keyed by pool

def parse_settings():
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
        
        parsed_settings[i]['exclude'] = settings['exclude'].lower().split(',')
        parsed_settings[i]['pool'] = int(settings['pool'])
        try:
            bn_ids[parsed_settings[i]['pool']].append(i)
        except KeyError:
            bn_ids[parsed_settings[i]['pool']] = []
            bn_ids[parsed_settings[i]['pool']].append(i)

def bn_to_pool(bn):
    return parsed_settings[bn.id]['pool']
    
def list_of_bnet_objects(pool):
    ret = []
    for i in bn_ids[pool]:
        ret.append(bnet.bnets[i])
    return ret
    
def clantags_in_pool(pool):
    return [clantags[j] for j in bn_ids[pool]]
    
clantags = {} # keyed by bnet id
cookies = {} # keyed by bnet id
clanmembers = {} # keyed by pool

class ClanMemberStatus:
    def __init__(self, rank, online):
        self.rank = rank
        self.online = online

def is_excluded(pool, username):
    for i in bn_ids[pool]:
        if username.lower() in parsed_settings[i]['exclude']:
            return True
    return False

def get_online_clanmembers(bn):
    onlinenames = []
    pool = bn_to_pool(bn)
    for i in clanmembers[pool]:
        if clanmembers[pool][i].online and not is_excluded(pool, i):
            onlinenames.append(i)
    onlinenames.sort()
    
    return onlinenames
    
def get_clanmember_rank(bn, name):
    pool = bn_to_pool(bn)
    member = clanmembers[pool].get(name, None)
    if member:
        return member.rank
    else:
        return -1

def got_claninfo(bn, d):
    clantags[bn.id] = str(d.tag)
    
    cookie = rand.randint(0, 2147483647)
    cookies[bn.id] = cookie
    bn.send_packet(bnetprotocol.SEND_SID_CLANMEMBERLIST(cookie))

def clannie_statuschange(bn, d):
    pool = bn_to_pool(bn)
    clanmembers[pool][str(d.username)] = ClanMemberStatus(d.rank, 1 if d.status > 0 else 0)
    
def clannie_removed(bn, d):
    pool = bn_to_pool(bn)
    del clanmembers[pool][str(d)]
    
def got_clanlist(bn, d):
    if d.cookie != cookies[bn.id]:
        return
        
    pool = bn_to_pool(bn)
    for i in d.memberlist:
        username = str(i.username)
        try:
            clanmembers[pool][username] = ClanMemberStatus(i.rank, i.online)
        except KeyError:
            clanmembers[pool] = {}
            clanmembers[pool][username] = ClanMemberStatus(i.rank, i.online)

def install():
    parse_settings()
    hook.register('after-handle_sid_clanmemberlist', got_clanlist)
    hook.register('after-handle_sid_claninfo', got_claninfo)
    hook.register('after-handle_sid_clanmemberstatuschange', clannie_statuschange)
    hook.register('after-handle_sid_clanmemberremoved', clannie_removed)

def uninstall():
    hook.unregister('after-handle_sid_clanmemberlist', got_clanlist)
    hook.unregister('after-handle_sid_claninfo', got_claninfo)
    hook.unregister('after-handle_sid_clanmemberstatuschange', clannie_statuschange)
    hook.unregister('after-handle_sid_clanmemberremoved', clannie_removed)