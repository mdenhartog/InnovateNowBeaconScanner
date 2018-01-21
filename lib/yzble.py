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
# pylint: disable=E0401,C0103

""" BLE scanner for beacons and tags """

import binascii
import logging
from machine import Timer
from network import Bluetooth

# Initialize logging
try:
    import config
    logging.basicConfig(level=config.LOG_LEVEL)
except ImportError:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class Scanner(object):
    """ BLE scanner for beacons and tags data packages """

    def __init__(self, max_list_items=25):

        self._beacons = []
        self._itags = []

        self._max_list_items = max_list_items
        self._ble = None

        # This part is added due to a bug in firmware 1.10.2b1
        self._alarm = None

    def _alarm_handler(self, alarm):
        """ Handler for the alarm, stop scanning """
        if self._ble:
            self._ble.stop_scan()
        alarm.cancel()

    def start(self, timeout=-1):
        """ Start beacon scanning """

        logger.info('Start scanning for beacons and tags')
        if self._ble is None:
            self._ble = Bluetooth()

        # Start the alarm to stop the BLE scanning
        self._alarm = Timer.Alarm(self._alarm_handler, timeout)

        self._ble.start_scan(timeout)
        while self._ble.isscanning():
            self.beacon_data_collect()

    def stop(self):
        """ Stop BLE """
        logger.info('Stop scanning for beacons and tags')
        if self._ble:
            self._ble.stop_scan()
            self._ble.deinit()
            self._ble = None

    def set_max_list_items(self, max_list_items):
        """ Set the max list items to return"""
        self._max_list_items = max_list_items

    def reset(self):
        """ Reset the retrieved beacon/tag list during scanning """
        logger.info('Reset found beacon/itag list')
        self._beacons[:] = []
        self._itags[:] = []

    @property
    def beacons(self):
        """ Return the beacons found """
        res = list(self._beacons) # make a copy
        return res

    @property
    def itags(self):
        """ Return the itags found """
        res = list(self._itags) # make a copy
        return res

    def beacon_data_collect(self):
        """ Collect the beacon data """

        adv = self._ble.get_adv()
        if adv:

            if self._ble.resolve_adv_data(adv.data, Bluetooth.ADV_NAME_CMPL) == "ITAG":

                binitag = binascii.hexlify(adv[0])
                itag = binitag.decode('UTF-8')

                if itag not in self._itags:
                    logger.debug('Found tag [%s]', itag)
                    self._itags.append(itag)

            else:

                # try to get the complete name only works with ibeacons
                data = self._ble.resolve_adv_data(adv.data, Bluetooth.ADV_MANUFACTURER_DATA)

                if data:
                    # try to get the manufacturer data (Apple's iBeacon data is sent here)
                    bindata = binascii.hexlify(data)
                    beacon = bindata.decode('UTF-8')

                    # Check if beacon is in list
                    if beacon not in self._beacons:
                        logger.debug('Found beacon [%s]', beacon)
                        self._beacons.append(beacon)
