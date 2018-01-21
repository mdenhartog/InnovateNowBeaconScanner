# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Linter
# pylint: disable=E0401,E1101,C0103

"""
Yeezz Beacon Scanner boot configuration
"""

import os
import machine
import pycom

from network import Server
from config import SERIAL_ACCESS
from config import FTP_ACCESS
from config import FTP_USER
from config import FTP_PASSWORD

# Deactivate heartbeat
pycom.heartbeat(False)

# Activate Serial Access
if SERIAL_ACCESS:
    uart = machine.UART(0, 115200)
    os.dupterm(uart)

# Disable FTP server
server = Server()
server.deinit()

# Enable the server again with new settings
if FTP_ACCESS:
    server.init(login=(FTP_USER, FTP_PASSWORD), timeout=600)

# Wifi on boot default off
pycom.wifi_on_boot(False)
