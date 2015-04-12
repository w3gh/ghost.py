from struct import pack, unpack
from collections import namedtuple

BNET_HEADER_CONSTANT = b'\xff'

SID_AUTH_INFO              = b'\x50'
SID_PING                   = b'\x25'
SID_AUTH_CHECK             = b'\x51'
SID_REQUIREDWORK           = b'\x4c'
SID_AUTH_ACCOUNTLOGON      = b'\x53'
SID_AUTH_ACCOUNTLOGONPROOF = b'\x54'
SID_NULL                   = b'\x00'
SID_NETGAMEPORT            = b'\x45'
SID_ENTERCHAT              = b'\x0a'
SID_JOINCHANNEL            = b'\x0c'
SID_CHATEVENT              = b'\x0f'
SID_CHATCOMMAND            = b'\x0e'
SID_CLANINFO               = b'\x75'
SID_CLANMEMBERLIST         = b'\x7d'
SID_CLANMEMBERSTATUSCHANGE = b'\x7f'
SID_MESSAGEBOX             = b'\x19'
SID_CLANINVITATION         = b'\x77'
SID_CLANMEMBERREMOVED      = b'\x7e'
SID_FRIENDSUPDATE          = b'\x66'
SID_FRIENDSLIST            = b'\x65'
SID_FLOODDETECTED          = b'\x13'
SID_FRIENDSADD             = b'\x67'

KR_GOOD             = b'\x00\x00\x00\x00'
KR_OLD_GAME_VERSION = b'\x00\x01\x00\x00'
KR_INVALID_VERSION  = b'\x01\x01\x00\x00'
KR_ROC_KEY_IN_USE   = b'\x01\x02\x00\x00'
KR_TFT_KEY_IN_USE   = b'\x11\x02\x00\x00'

NULL   = b'\x00'
NULL_2 = b'\x00\x00'
NULL_3 = b'\x00\x00\x00'
NULL_4 = b'\x00\x00\x00\x00'

EID_SHOWUSER            = b'\x01\x00\x00\x00'
EID_JOIN                = b'\x02\x00\x00\x00'
EID_LEAVE               = b'\x03\x00\x00\x00'
EID_WHISPER             = b'\x04\x00\x00\x00'
EID_TALK                = b'\x05\x00\x00\x00'
EID_BROADCAST           = b'\x06\x00\x00\x00'
EID_CHANNEL             = b'\x07\x00\x00\x00'
EID_USERFLAGS           = b'\x09\x00\x00\x00'
EID_WHISPERSENT         = b'\x0a\x00\x00\x00'
EID_CHANNELFULL         = b'\x0d\x00\x00\x00'
EID_CHANNELDOESNOTEXIST = b'\x0e\x00\x00\x00'
EID_CHANNELRESTRICTED   = b'\x0f\x00\x00\x00'
EID_INFO                = b'\x12\x00\x00\x00'
EID_ERROR               = b'\x13\x00\x00\x00'
EID_EMOTE               = b'\x17\x00\x00\x00'

CLANRANK_INITIATE       = 0
CLANRANK_PEON           = 1
CLANRANK_GRUNT          = 2
CLANRANK_SHAMAN         = 3
CLANRANK_CHIEFTAN       = 4

# Bitfield
FRIENDSTATUS_MUTUAL     = 1
FRIENDSTATUS_DND        = 2
FRIENDSTATUS_AWAY       = 4

# Value
FRIENDLOCATION_OFFLINE  = 0
FRIENDLOCATION_NOTCHAT  = 1
FRIENDLOCATION_CHAT     = 2
FRIENDLOCATION_PUB      = 3
FRIENDLOCATION_PRIVHIDE = 4
FRIENDLOCATION_PRIVSHOW = 5

def assign_length(p):
    l = len(p)
    #p[2] = l % 256
    #p[3] = l / 256
    p[2:4] = pack('<H', l)

def get_length(p):
    return unpack('<H', str(p[2:4]))[0]

def validate_length(p):
    return len(p) == get_length(p)

def SEND_SID_PING(payload):
    p = bytearray()
    p.extend(BNET_HEADER_CONSTANT)
    p.extend(SID_PING)
    p.extend(NULL_2)
    p.extend(payload)
    
    assign_length(p)
    return p

def SEND_PROTOCOL_INITIALIZE_SELECTOR():
    return bytearray(b'\x01')

def SEND_SID_AUTH_INFO(ver, tft, localeId, countryAbbrev, country):
    p = bytearray()
    
    # possible TODO: make these configurable
    protocolId = NULL_4
    platformId = b'68XI'
    productIdRoc = b'3RAW'
    productIdTft = b'PX3W'
    version = bytearray(); version.append(ver); version.extend(NULL_3)
    language = b'SUne'
    localIp = b'\x7f\x00\x00\x01'
    timeZoneBias = b'\x2c\x01\x00\x00'

    p.extend(BNET_HEADER_CONSTANT)
    p.extend(SID_AUTH_INFO)
    p.extend(NULL_2) # length
    p.extend(protocolId)
    p.extend(platformId)
    p.extend(productIdTft if tft else productIdRoc)
    p.extend(version)
    p.extend(localIp)
    p.extend(language)
    p.extend(timeZoneBias)
    p.extend(pack('<I', localeId)) # locale (3081 (en-au) for me)
    p.extend(pack('<I', localeId)) # language (1033 (en-us) for me)
    p.extend(countryAbbrev); p.extend(NULL)
    p.extend(country); p.extend(NULL)
    
    assign_length(p)
    return p

def SEND_SID_AUTH_CHECK(tft, clientToken, exeVersion, exeVersionHash, keyInfoRoc, keyInfoTft, exeInfo, keyOwnerName):
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_AUTH_CHECK)
    p.extend(NULL_2) # length
    p.extend(clientToken)
    p.extend(exeVersion)
    p.extend(exeVersionHash)
    numKeys = 2 if tft else 1
    p.append(numKeys); p.extend(NULL_3)
    p.extend(NULL_4) # boolean Using Spawn (32 bit)
    p.extend(keyInfoRoc)
    if tft:
        p.extend(keyInfoTft)
    p.extend(exeInfo); p.append(NULL)
    p.extend(keyOwnerName); p.append(NULL)

    assign_length(p)
    return p

def SEND_SID_AUTH_ACCOUNTLOGON(clientPublicKey, accountName):
    assert len(clientPublicKey) == 32
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_AUTH_ACCOUNTLOGON)
    p.extend(NULL_2) # length
    p.extend(clientPublicKey) #; p.append(NULL)
    p.extend(accountName); p.append(NULL)
    
    assign_length(p)
    return p

def SEND_SID_AUTH_ACCOUNTLOGONPROOF(M1):
    assert len(M1) == 20
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_AUTH_ACCOUNTLOGONPROOF)
    p.extend(NULL_2) # length
    p.extend(M1)

    assign_length(p)
    return p

def SEND_SID_NETGAMEPORT(serverPort):
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_NETGAMEPORT)
    p.extend(NULL_2) # length
    p.extend(pack('<H', serverPort))

    assign_length(p)
    return p

def SEND_SID_ENTERCHAT():
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_ENTERCHAT)
    p.extend(NULL_2) # length
    p.append(NULL) # account name
    p.append(NULL) # stat string
    
    assign_length(p)
    return p

def SEND_SID_JOINCHANNEL(channel):
    noCreateJoin = b'\x02\x00\x00\x00'
    firstJoin = b'\x01\x00\x00\x00'
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_JOINCHANNEL)
    p.extend(NULL_2) # length
    if len(channel) > 0:
        p.extend(noCreateJoin)
    else:
        p.extend(firstJoin)
    p.extend(channel); p.append(NULL)
    
    assign_length(p)
    return p

def SEND_SID_CHATCOMMAND(command):
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_CHATCOMMAND)
    p.extend(NULL_2) # length
    p.extend(command); p.append(NULL)
    
    assign_length(p)
    return p
    
def SEND_SID_CLANMEMBERLIST(cookie):
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_CLANMEMBERLIST)
    p.extend(NULL_2) # length
    p.extend(pack('<I', cookie))
    
    assign_length(p)
    return p

def SEND_SID_CLANINVITATION(cookie, user):
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_CLANINVITATION)
    p.extend(NULL_2)
    p.extend(pack('<I', cookie))
    p.extend(user); p.append(NULL)
    
    assign_length(p)
    return p
    
def SEND_SID_FRIENDSLIST():
    p = bytearray()
    p.append(BNET_HEADER_CONSTANT)
    p.append(SID_FRIENDSLIST)
    p.extend(NULL_2)
    
    assign_length(p)
    return p
    
def RECEIVE_SID_PING(p):
    assert (validate_length(p) and len(p) >= 8)
    return bytes(p[4:8])

def RECEIVE_SID_REQUIREDWORK(p):
    return validate_length(p)

SidAuthInfo = namedtuple('SidAuthInfo', ('logonType', 'serverToken', 'mpqFileTime', 'ix86VerFileName', 'valueStringFormula'))

def RECEIVE_SID_AUTH_INFO(p):
    assert (validate_length(p) and len(p) >= 25)
    logonType = p[4:8]
    serverToken = p[8:12]
    mpqFileTime = p[16:24]
    ix86VerFileName = p[24:].split(NULL, 1)[0]
    valueStringFormula = p[25 + len(ix86VerFileName):].split(NULL, 1)[0]
    return SidAuthInfo(logonType, serverToken, mpqFileTime, ix86VerFileName, valueStringFormula)

SidAuthCheck = namedtuple('SidAuthCheck', ('keyState', 'keyStateDescription'))

def RECEIVE_SID_AUTH_CHECK(p):
    assert (validate_length(p) and len(p) >= 9)
    keyState = bytes(p[4:8])
    keyStateDescription = p[5:].split(NULL, 1)[0]
    return SidAuthCheck(keyState, keyStateDescription)

SidAuthAccountlogon = namedtuple('SidAuthAccountlogon', ('status', 'salt', 'serverPublicKey'))

def RECEIVE_SID_AUTH_ACCOUNTLOGON(p):
    assert (validate_length(p) and len(p) >= 8)
    status = bytes(p[4:8])
    if not (status == NULL_4 and len(p) >= 72):
        return False
    salt = bytes(p[8:40])
    serverPublicKey = bytes(p[40:72])
    return SidAuthAccountlogon(status, salt, serverPublicKey)

def RECEIVE_SID_AUTH_ACCOUNTLOGONPROOF(p):
    assert (validate_length(p) and len(p) >= 8)
    status = bytes(p[4:8])
    return (status == NULL_4 or status == b'\x0e000000')

def RECEIVE_SID_NULL(p):
    return validate_length(p)

def RECEIVE_SID_ENTERCHAT(p):
    assert (validate_length(p) and len(p) >= 5)
    return bytes(p[4:])

SidChatEvent = namedtuple('SidChatEvent', ('event', 'ping', 'user', 'message'))

def RECEIVE_SID_CHATEVENT(p):
    assert (validate_length(p) and len(p) >= 20)
    event = p[4:8]
    ping = p[12:16]
    user = p[28:].split(NULL, 1)[0]
    message = p[29 + len(user):].split(NULL, 1)[0]
    return SidChatEvent(event, ping, user, message)

SidClanInfo = namedtuple('SidClanInfo', ('tag', 'rank'))
# rank: 0 = < 1 week, 1 = > 1 week, 2 = member, 3 = officer, 4 = leader

def RECEIVE_SID_CLANINFO(p):
    assert (validate_length(p) and len(p) >= 8)
    tag = p[5:9][::-1]
    rank = p[9]
    return SidClanInfo(tag, rank)

ClanMember = namedtuple('ClanMember', ('username', 'rank', 'online', 'location'))
SidClanMemberList = namedtuple('SidClanMemberList', ('cookie', 'count', 'memberlist'))

def RECEIVE_SID_CLANMEMBERLIST(p):
    assert validate_length(p)
    cookie, = unpack('<I', str(p[4:8]))
    count = p[8]
    memberlist = []
    
    pointer = 9
    for i in xrange(count):
        username = p[pointer:].split(NULL, 1)[0]
        pointer += len(username) + 1
        rank = p[pointer]
        pointer += 1
        online = p[pointer]
        pointer += 1
        location = p[pointer:].split(NULL, 1)[0]
        pointer += len(location) + 1
        memberlist.append(ClanMember(username, rank, online, location))
        
    return SidClanMemberList(cookie, count, memberlist)

SidClanMemberStatusChange = namedtuple('SidClanMemberStatusChange', ('username', 'rank', 'status', 'location'))
# location:
# 19 = just logged on
# 

def RECEIVE_SID_CLANMEMBERSTATUSCHANGE(p):
    assert validate_length(p)
    pointer = 4
    username = p[pointer:].split(NULL, 1)[0]
    pointer += len(username) + 1
    rank = p[pointer]
    pointer += 1
    status = p[pointer]
    pointer += 1
    location = p[pointer:].split(NULL, 1)[0]
    pointer += len(location) + 1
    
    return SidClanMemberStatusChange(username, rank, status, pointer)

SidMessageBox = namedtuple('SidMessageBox', ('style', 'text', 'caption'))
def RECEIVE_SID_MESSAGEBOX(p):
    assert validate_length(p)
    style = unpack('<I', str(p[4:8]))
    pointer = 8
    text = p[pointer:].split(NULL, 1)[0]
    pointer += len(text) + 1
    caption = p[pointer:].split(NULL, 1)[0]
    pointer += len(caption) + 1
    
    return SidMessageBox(style, text, caption)
    
SidClanInvitation = namedtuple('SidClanInvitation', ('cookie', 'result'))
def RECEIVE_SID_CLANINVITATION(p):
    assert validate_length(p)
    print str(len(p[4:9]))
    cookie, result = unpack('<IB', str(p[4:9]))
    
    return SidClanInvitation(cookie, result)
    
def RECEIVE_SID_CLANMEMBERREMOVED(p):
    assert validate_length(p)
    return str(p[4:-1])
    
FriendUpdateUnit = namedtuple('FriendUpdateUnit', ('status', 'location', 'productid', 'longlocation'))
def _decode_friendupdate_unit(data):
    pointer = 0
    print repr(data)
    status, location = unpack('<BB', str(data[pointer:pointer+2]))
    pointer += 2
    productid = str(data[pointer:pointer+4])[::-1]
    pointer += 4
    longlocation = str(data[pointer:].split(NULL, 1)[0])
    pointer += len(longlocation) + 1
    
    # at this point, pointer = number of bytes that were consumed
    return (pointer, FriendUpdateUnit(status, location, productid, longlocation))

SidFriendsUpdate = namedtuple('SidFriendsUpdate', ('number', 'update'))
def RECEIVE_SID_FRIENDSUPDATE(p):
    assert validate_length(p)
    pointer = 4
    number = p[pointer]
    pointer += 1
    return SidFriendsUpdate(number, _decode_friendupdate_unit(p[pointer:])[1])
    
def RECEIVE_SID_FRIENDSLIST(p):
    assert validate_length(p)
    entries = p[4]
    pointer = 5
    friendlist = {}
    for i in xrange(entries):
        name = p[pointer:].split(NULL, 1)[0]
        pointer += len(name) + 1
        bytes_consumed, update = _decode_friendupdate_unit(p[pointer:])
        pointer += bytes_consumed
        friendlist[str(name)] = SidFriendsUpdate(i, update)
    return friendlist
    
def RECEIVE_SID_FLOODDETECTED(p):
    assert validate_length(p)
    return None
    
SidFriendsAdd = namedtuple('SidFriendsAdd', ('account', 'type', 'status', 'product', 'location'))
def RECEIVE_SID_FRIENDSADD(p):
    assert validate_length(p)
    pointer = 4
    account = p[pointer:].split(NULL, 1)[0]
    pointer += len(account) + 1
    type = p[pointer]
    pointer += 1
    status = p[pointer]
    pointer += 1
    product = p[pointer:pointer + 4]
    pointer += 4
    location = p[pointer:].split(NULL, 1)[0]
    pointer += len(location) + 1
    
    return SidFriendsAdd(account, type, status, product, location)
    
    
receivers = {
    SID_AUTH_INFO:              RECEIVE_SID_AUTH_INFO,
    SID_AUTH_CHECK:             RECEIVE_SID_AUTH_CHECK,
    SID_PING:                   RECEIVE_SID_PING,
    SID_REQUIREDWORK:           RECEIVE_SID_REQUIREDWORK,
    SID_AUTH_ACCOUNTLOGON:      RECEIVE_SID_AUTH_ACCOUNTLOGON,
    SID_AUTH_ACCOUNTLOGONPROOF: RECEIVE_SID_AUTH_ACCOUNTLOGONPROOF,
    SID_NULL:                   RECEIVE_SID_NULL,
    SID_ENTERCHAT:              RECEIVE_SID_ENTERCHAT,
    SID_CHATEVENT:              RECEIVE_SID_CHATEVENT,
    SID_CLANINFO:               RECEIVE_SID_CLANINFO,
    SID_CLANMEMBERLIST:         RECEIVE_SID_CLANMEMBERLIST,
    SID_CLANMEMBERSTATUSCHANGE: RECEIVE_SID_CLANMEMBERSTATUSCHANGE,
    SID_MESSAGEBOX:             RECEIVE_SID_MESSAGEBOX,
    SID_CLANINVITATION:         RECEIVE_SID_CLANINVITATION,
    SID_CLANMEMBERREMOVED:      RECEIVE_SID_CLANMEMBERREMOVED,
    SID_FRIENDSUPDATE:          RECEIVE_SID_FRIENDSUPDATE,
    SID_FRIENDSLIST:            RECEIVE_SID_FRIENDSLIST,
    SID_FLOODDETECTED:          RECEIVE_SID_FLOODDETECTED,
}
