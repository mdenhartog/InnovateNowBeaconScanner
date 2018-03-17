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
# pylint: disable=E0401,C0103,R0903

"""
InnovateNow Core Network Library
"""

import sys
import time
import machine

from network import WLAN

# Initialize logging
import inlogging as logging
log = logging.getLogger(__name__)

class WLANNetwork(object):
    """
    Class manage the WLAN network
    """

    def __init__(self, ssid=None, key=None, antenna=WLAN.INT_ANT):
        """
        Initialization of the WLAN network
        """
        self.ssid = ssid
        self.key = key
        self.antenna = antenna
        self.wlan = None

    @property
    def is_connected(self):
        """
        Return if the WLAN is connected
        """
        return self.wlan.isconnected()

    def connect(self):
        """
        Establish a WLAN connection to the specified SSID
        """
        log.info('Connect to WLAN [' + self.ssid + ']')

        if self.wlan is None:

            # Init WLAN
            wlan = WLAN(mode=WLAN.STA, antenna=self.antenna)

            # Scan for available accesspoints
            nets = wlan.scan()

            for net in nets:
                if net.ssid == self.ssid:

                    # Connect to the network
                    wlan.connect(self.ssid, (net.sec, self.key), timeout=10000)
                    while not wlan.isconnected():
                        machine.idle() # Save power while waiting

                    self.wlan = wlan
                    log.debug("ipconfig:" + str(self.wlan.ifconfig()))
                    break

            if self.wlan is None:
                log.error('Error establishing connection to wlan [' + self.ssid + ']')
                raise IOError('Network connection to wlan [' + self.ssid + '] failed')

    def disconnect(self):
        """
        Disconnect the WLAN
        """
        log.info('Disconnect from WLAN [' + self.ssid + ']')

        if self.wlan:
            if self.wlan.isconnected():
                self.wlan.disconnect()
                self.wlan.deinit()
                self.wlan = None

    def reconnect(self):
        """
        Reconnect the WLAN
        """
        self.disconnect()
        self.connect()


class NTP(object):
    """
    Class for syncing device time with the NTP
    """
    def __init__(self, ntp_pool_server='pool.ntp.org'):
        """
        Initialize time via NTP
        """
        self.ntp_pool_server = ntp_pool_server

    def sync(self):
        """
        Sync with network time
        """
        rtc = machine.RTC()
        rtc.ntp_sync(self.ntp_pool_server, update_period=3600)
        while not rtc.synced():
            time.sleep(1)
