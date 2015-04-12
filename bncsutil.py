from ctypes import *
from collections import namedtuple
import platform

import nativethread
from misc import *

_libbncsutil = None
_utilthread = None

def init(force=False):
    global _libbncsutil, _utilthread
    if _libbncsutil is None or _utilthread is None or force:
        # _utilthread = nativethread.ReservedThread()
        _utilthread = nativethread.DummyThread()
        
        system = platform.system()
        if system == 'Windows':
            _libbncsutil = _utilthread.execute(WinDLL, 'BNCSutil.dll')
        elif system == 'Linux':
            _libbncsutil = _utilthread.execute(CDLL, 'libbncsutil.so')
        else:
            atomic_debug('%s: Unsupported system. Assuming Unix-like.' % (__file__))
            _libbncsutil = _utilthread.execute(CDLL, 'libbncsutil.so')

PLATFORM_X86 = 1

ExeInfo = namedtuple('ExeInfo', ('exe_info', 'version'))

@DebugCall
def extractMPQNumber(mpqName):
    init()
    global _libbncsutil, _utilthread
    return _utilthread.execute(_libbncsutil.extractMPQNumber, mpqName)

@DebugCall
def getExeInfo(file_name, platform):
    init()
    global _libbncsutil, _utilthread
    exe_info = create_string_buffer(256)
    version = c_uint()
    _utilthread.execute(_libbncsutil.getExeInfo, file_name, byref(exe_info), 256, byref(version), platform)
    return ExeInfo(exe_info.value.replace(b'/110', b'/10'), version.value) # hack needed for :reason:

@DebugCall
def checkRevisionFlat(valueString, file1, file2, file3, mpqNumber):
    init()
    global _libbncsutil, _utilthread
    checksum = c_uint()
    _utilthread.execute(_libbncsutil.checkRevisionFlat, valueString, file1, file2, file3, mpqNumber, byref(checksum))
    return checksum.value

CdKey = namedtuple('CdKey', ('public_value', 'product', 'hash'))

@DebugCall
def kd_quick(cd_key, client_token, server_token):
    init()
    global _libbncsutil, _utilthread
    public_value = c_uint()
    product = c_uint()
    hash_buffer = create_string_buffer(256)
    _utilthread.execute(_libbncsutil.kd_quick, cd_key, client_token, server_token, byref(public_value), byref(product), byref(hash_buffer), 256)
    return CdKey(public_value.value, product, hash_buffer.value)

@DebugCall
def nls_init(username, password):
    init()
    global _libbncsutil, _utilthread
    return _utilthread.execute(_libbncsutil.nls_init_l, username, len(username), password, len(password))

@DebugCall
def nls_get_A(nls):
    init()
    global _libbncsutil, _utilthread
    buffer = create_string_buffer(32)
    _utilthread.execute(_libbncsutil.nls_get_A, nls, byref(buffer))
    # atomic_debug('nls_get_A: ' + repr(buffer.value))
    return buffer.value

@DebugCall
def nls_get_M1(nls, B, salt):
    init()
    global _libbncsutil, _utilthread
    buffer = create_string_buffer(20)
    _utilthread.execute(_libbncsutil.nls_get_M1, nls, byref(buffer), B, salt)
    return buffer.value

@DebugCall
def hash_password(password):
    init()
    global _libbncsutil, _utilthread
    buffer = create_string_buffer(20)
    _utilthread.execute(_libbncsutil.hashPassword, password, byref(buffer))
    return buffer.value