# ghost.py
Warcraft 3 Battle.net python bot

======
All OS
======

You need to copy game.dll, Storm.dll and war3.exe from your Warcraft III installation.
You need Python 2.7 installed (might work with 2.6 as well).

If you are using 64-bit Python, grab Base and Greenlet from http://www.lfd.uci.edu/~gohlke/pythonlibs/
If you are using 32-bit Python, you can grab greenlet and eventlet from PyPI or the link above.
If you are using Lunix, use pip to install eventlet.

Copy default.cfg to gghost.cfg and make your changes there. You should prefer to keep default.cfg
clean so that it can be automatically updated.

To start gGHost, run launch.py.

=======
Windows
=======

You need to copy BNCSutil.dll from https://github.com/w3gh/bncsutil

=====
Linux
=====

Compile libbncsutil.so from https://github.com/w3gh/bncsutil

====
Bugs
====

For some reason, calling BNCSUtil sometimes fail, and that will show as an AssertionError relating
to CD Key hashes.

