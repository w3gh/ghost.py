import string
import eventlet, eventlet.patcher
eventlet.patcher.monkey_patch(socket=True)
import socket

import time
from struct import pack, unpack
from collections import deque
from random import SystemRandom
rand = SystemRandom()

import nativethread
import bnetprotocol
import bncsutil
from misc import *
import hook

# Global
bnets = []

def create_key_info(key, clientToken, serverToken): # str, int, int
    public_value, product, hash = bncsutil.kd_quick(key, clientToken, serverToken)
    atomic_debug(repr((public_value, product, hash)))
    p = bytearray()
    p.extend(pack('<I', len(key)))
    p.extend(pack('<I', product.value))
    p.extend(pack('<I', public_value))
    p.extend(b'\x00\x00\x00\x00')
    p.extend(hash)
    return p

class BNet:
    def __init__(self):
        self.incoming_packets = deque()
        self.incoming_buffer = bytearray()

        self.clientToken = b'\xdc\x01\xcb\x07'

        self.floodControl = False
        self.lastPacketTime = 0
        self.packetInterval = 4.0

        self.handlers = {
            bnetprotocol.SID_PING:                      self.HANDLE_SID_PING,
            bnetprotocol.SID_AUTH_INFO:                 self.HANDLE_SID_AUTH_INFO,
            bnetprotocol.SID_AUTH_CHECK:                self.HANDLE_SID_AUTH_CHECK,
            bnetprotocol.SID_REQUIREDWORK:              self.HANDLE_SID_REQUIREDWORK,
            bnetprotocol.SID_AUTH_ACCOUNTLOGON:         self.HANDLE_SID_AUTH_ACCOUNTLOGON,
            bnetprotocol.SID_AUTH_ACCOUNTLOGONPROOF:    self.HANDLE_SID_AUTH_ACCOUNTLOGONPROOF,
            bnetprotocol.SID_NULL:                      self.HANDLE_SID_NULL,
            bnetprotocol.SID_ENTERCHAT:                 self.HANDLE_SID_ENTERCHAT,
            bnetprotocol.SID_CHATEVENT:                 self.HANDLE_SID_CHATEVENT,
            bnetprotocol.SID_CLANINFO:                  self.HANDLE_SID_CLANINFO,
            bnetprotocol.SID_CLANMEMBERLIST:            self.HANDLE_SID_CLANMEMBERLIST,
            bnetprotocol.SID_CLANMEMBERSTATUSCHANGE:    self.HANDLE_SID_CLANMEMBERSTATUSCHANGE,
            bnetprotocol.SID_MESSAGEBOX:                self.HANDLE_SID_MESSAGEBOX,
            bnetprotocol.SID_CLANINVITATION:            self.HANDLE_SID_CLANINVITATION,
            bnetprotocol.SID_CLANMEMBERREMOVED:         self.HANDLE_SID_CLANMEMBERREMOVED,
            bnetprotocol.SID_FRIENDSUPDATE:             self.HANDLE_SID_FRIENDSUPDATE,
            bnetprotocol.SID_FRIENDSLIST:               self.HANDLE_SID_FRIENDSLIST,
            bnetprotocol.SID_FLOODDETECTED:             self.HANDLE_SID_FLOODDETECTED,
            bnetprotocol.SID_FRIENDSADD:                self.HANDLE_SID_FRIENDSADD,
        }

    def handshake(self):
        p = bnetprotocol.SEND_PROTOCOL_INITIALIZE_SELECTOR()
        self.send_packet(p)

        p = bnetprotocol.SEND_SID_AUTH_INFO(self.war3version, self.tft, self.localeId, self.countryAbbrev, self.country)
        self.send_packet(p)

    def send_packet(self, p, immediate=False):
        if self.floodControl and not immediate:
            while time.time() < self.lastPacketTime + self.packetInterval:
                atomic_print('Flood controlled message: %s' % str(p).encode('hex'))
                eventlet.sleep(self.packetInterval)
        self.lastPacketTime = time.time()
        atomic_print('>' + str(p).encode('hex'))
        self.socket.sendall(p)

    def HANDLE_SID_PING(self, d):
        self.send_packet(bnetprotocol.SEND_SID_PING(d))

    def HANDLE_SID_AUTH_INFO(self, d):
        #atomic_debug('In HANDLE_SID_AUTH_INFO')
        #exeInfo, exeVersion = tpool.execute(bncsutil.getExeInfo, self.war3exePath, bncsutil.PLATFORM_X86)
        exeInfo, exeVersion = bncsutil.getExeInfo(self.war3exePath, bncsutil.PLATFORM_X86)
        exeVersion = pack('<I', exeVersion)
        #exeVersionHash = tpool.execute(bncsutil.checkRevisionFlat, bytes(d.valueStringFormula), self.war3exePath, self.stormdllPath, self.gamedllPath, bncsutil.extractMPQNumber(bytes(d.ix86VerFileName)))
        exeVersionHash = bncsutil.checkRevisionFlat(bytes(d.valueStringFormula), self.war3exePath, self.stormdllPath, self.gamedllPath, bncsutil.extractMPQNumber(bytes(d.ix86VerFileName)))
        keyInfoRoc = ''
        keyInfoRoc = create_key_info(self.keyRoc, unpack('<I', self.clientToken)[0], unpack('<I', bytes(d.serverToken))[0])
        if len(keyInfoRoc) != 36:
            bncsutil.init(force=True)
            keyInfoRoc = create_key_info(self.keyRoc, unpack('<I', self.clientToken)[0], unpack('<I', bytes(d.serverToken))[0])
        assert len(keyInfoRoc) == 36
        keyInfoTft = ''
        if self.tft:
            keyInfoTft = create_key_info(self.keyTft, unpack('<I', self.clientToken)[0], unpack('<I', bytes(d.serverToken))[0])
            if len(keyInfoTft) != 36:
                bncsutil.init(force=True)
                keyInfoTft = create_key_info(self.keyTft, unpack('<I', self.clientToken)[0], unpack('<I', bytes(d.serverToken))[0])
            assert len(keyInfoTft) == 36
        p = bnetprotocol.SEND_SID_AUTH_CHECK(self.tft, self.clientToken, exeVersion, pack('<I', exeVersionHash), keyInfoRoc, keyInfoTft, exeInfo, 'GHost')
        self.send_packet(p)

    def HANDLE_SID_AUTH_CHECK(self, d):
        # check, then SEND_SID_AUTH_ACCOUNTLOGON
        if d.keyState != bnetprotocol.KR_GOOD:
            atomic_debug('CD Key or version problem. See above.')
            self.socket.close()
        else:
            if self.__dict__.get('nls', None) is None:
                self.nls = bncsutil.nls_init(self.username, self.password)
            clientPublicKey = bncsutil.nls_get_A(self.nls)
            if len(clientPublicKey) != 32: # retry since bncsutil randomly fails
                bncsutil.init(force=True)
                self.nls = bncsutil.nls_init(self.username, self.password)
                clientPublicKey = bncsutil.nls_get_A(self.nls)
                assert len(clientPublicKey) == 32
            p = bnetprotocol.SEND_SID_AUTH_ACCOUNTLOGON(clientPublicKey, self.username)
            self.send_packet(p)

    def HANDLE_SID_REQUIREDWORK(self, d):
        return

    def HANDLE_SID_AUTH_ACCOUNTLOGON(self, d):
        #p = bnetprotocol.SEND_SID_AUTH_ACCOUNTLOGONPROOF(bncsutil.nls_get_M1(self.nls, d.serverPublicKey, d.salt))
        p = bnetprotocol.SEND_SID_AUTH_ACCOUNTLOGONPROOF(bncsutil.hash_password(self.password))
        self.send_packet(p)

    def HANDLE_SID_AUTH_ACCOUNTLOGONPROOF(self, d):
        hook.call_wait('before-handle_sid_accountlogonproof', self, d)
        if not d:
            atomic_debug('Logon proof rejected.')
            self.socket.close()
            return
        hook.call_wait('before-handle_sid_accountlogonproof', self, d)
        #p = bnetprotocol.SEND_SID_NETGAMEPORT(self.hostPort)
        #self.send_packet(p)
        p = bnetprotocol.SEND_SID_ENTERCHAT()
        self.send_packet(p)
        hook.call_nowait('after-handle_sid_accountlogonproof', self, d)

    def HANDLE_SID_NULL(self, d):
        return

    def HANDLE_SID_ENTERCHAT(self, d):
        hook.call_wait('before-handle_sid_enterchat', self, d)
        if b'#' in d:
            atomic_debug('Warning: Account already logged in.')
        p = bnetprotocol.SEND_SID_JOINCHANNEL(self.firstChannel)
        self.send_packet(p)
        self.floodControl = True
        hook.call_nowait('after-handle_sid_enterchat', self, d)

    def HANDLE_SID_CHATEVENT(self, d):
        hook.call_nowait('after-handle_sid_chatevent', self, d)
        return

    def HANDLE_SID_CLANINFO(self, d):
        hook.call_nowait('after-handle_sid_claninfo', self, d)

    def HANDLE_SID_CLANMEMBERLIST(self, d):
        hook.call_nowait('after-handle_sid_clanmemberlist', self, d)

    def HANDLE_SID_CLANMEMBERSTATUSCHANGE(self, d):
        hook.call_nowait('after-handle_sid_clanmemberstatuschange', self, d)

    def HANDLE_SID_MESSAGEBOX(self, d):
        hook.call_nowait('after-handle_sid_messagebox', self, d)

    def HANDLE_SID_CLANINVITATION(self, d):
        hook.call_nowait('after-handle_sid_claninvitation', self, d)

    def HANDLE_SID_CLANMEMBERREMOVED(self, d):
        hook.call_nowait('after-handle_sid_clanmemberremoved', self, d)

    def HANDLE_SID_FRIENDSUPDATE(self, d):
        hook.call_nowait('after-handle_sid_friendsupdate', self, d)

    def HANDLE_SID_FRIENDSLIST(self, d):
        hook.call_nowait('after-handle_sid_friendslist', self, d)

    def HANDLE_SID_FLOODDETECTED(self, d):
        hook.call_nowait('after-handle_sid_flooddetected', self, d)

    def HANDLE_SID_FRIENDSADD(self, d):
        hook.call_nowait('after-handle_sid_friendsadd', self, d)

    def process_packets(self):
        try:
            while True:
                p = self.incoming_packets.popleft()
                atomic_print('<' + str(p).encode('hex'))
                type = bytes(p[1:2])
                d = bnetprotocol.receivers[type](p)
                if type == bnetprotocol.SID_CHATEVENT:
                    buf = '"%s" [%s] %s' % (d.user, d.event, d.message)
                    atomic_print(str(buf))
                else:
                    atomic_print(str(d))
                self.handlers[type](d)

        except IndexError:
            return

    def extract_packets(self):
        while len(self.incoming_buffer) >= 4:
            p = self.incoming_buffer
            if bytes(p[0:1]) != bnetprotocol.BNET_HEADER_CONSTANT:
                atomic_debug('Bad header constant in ' + str(self) + '. Was ' + str(p[0]).encode('hex') + '.\r\n' + str(p).encode('hex'))
                return
            l = bnetprotocol.get_length(p)
            if l < 4:
                atomic_debug('Packet too short in ' + str(self) + '\r\n' + str(p).encode('hex'))
                return
            if len(p) >= l:
                self.incoming_packets.append(p[:l])
                self.incoming_buffer = p[l:]
            else: # still waiting for rest of the packet
                return

    def run(self):
        self.socket = socket.create_connection((self.server, self.port), source_address=(self.bindaddress, self.bindport))
        self.handshake()
        while True:
            p = self.socket.recv(1024)
            if len(p) < 1:
                atomic_print('recv returned nothing')
                # TODO: schedule reconnect
                break
            self.incoming_buffer.extend(p)
            self.extract_packets()
            self.process_packets()

def launch():
    from config import config

    bnet_pool = eventlet.GreenPool()

    for i in xrange(9001): # race condition: will ignore the 9001st and subsequent battle.net entries in config
        try:
            settings = dict(config['bnet'].items() + config['bnet' + str(i)].items())
        except KeyError:
            break

        # print i
        path = string(settings.get('war3path','WAR3'))

#        if(path[-1] != '/'):
#            path += '/'

        bn = BNet()
        bn.id = i
        bn.war3version = int(settings.get('war3version', '26'))
        bn.tft = int(settings.get('tft', '1'))
        bn.localeId = int(settings.get('localeid', '1033'))
        bn.countryAbbrev = bytes(settings.get('countryabbrev', 'USA').decode('ascii'))
        bn.country = bytes(settings.get('country', 'United States').decode('ascii'))
        bn.war3exePath = bytes(settings.get('war3exepath', 'war3.exe').decode('ascii'))
        bn.stormdllPath = bytes(settings.get('stormdllpath', 'Storm.dll').decode('ascii'))
        bn.gamedllPath = bytes(settings.get('gamedllpath', 'game.dll').decode('ascii'))
        bn.keyRoc = bytes(settings.get('keyroc', 'FFFFFFFFFFFFFFFFFFFFFFFFFF').decode('ascii'))
        assert bn.keyRoc != b''
        bn.keyTft = bytes(settings.get('keytft', 'FFFFFFFFFFFFFFFFFFFFFFFFFF').decode('ascii'))
        assert bn.keyTft != b'' or not bn.tft
        bn.username = bytes(settings.get('username', '').decode('ascii'))
        assert bn.username != ''
        bn.password = bytes(settings.get('password', '').decode('ascii'))
        bn.firstChannel = bytes(settings.get('firstchannel', 'The Void').decode('ascii'))

        bn.server = str(settings.get('server', ''))
        assert bn.server != ''
        bn.port = int(settings.get('port', '6112'))
        bn.bindaddress = str(settings.get('bindaddress', ''))
        bn.bindport = int(settings.get('bindport', '0'))

        bnets.append(bn)
        bnet_pool.spawn(bn.run)
        # eventlet.sleep(10.) # HACK: I think bncsutil doesn't like being used by multiple different bnet transactions

    bnet_pool.waitall()
