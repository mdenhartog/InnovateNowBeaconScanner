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
# pylint: disable=C0103

"""
Yeezz Beacon Scanner program

Steps
--------------------------------------------
1. Connect to Wifi
2. Get time from NTP Server
3. Connect to AWS Yeezz IoT environment
4. Send alive signal
5. Scan for Beacons / Tags for the specified amount of time
6. Initialize GPS
7. Initialize Environment sensor
8. Send message to AWS Yeezz IoT Environment
9. Retrieve messages from AWS Yeezz IoT Enviroment for this device
10. Check for OTA updates (once a day)
"""

import logging
import machine
import config
import pycom
import gc

from version import VERSION
from yznetwork import WLANNetwork, NTP
from yzaws import AWS
from yzmsg import AliveMessage, GPSMessage, EnvironMessage, AWSMessage
from yzgps import GPS, DEFAULT_RX_PIN, DEFAULT_TX_PIN
from yzenvsensor import EnviromentalSensor

# Initialize logging
try:
    logging.basicConfig(level=config.LOG_LEVEL)
except ImportError:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# Led orange
pycom.rgbled(config.LED_COLOR_WARNING)

logger.info('Start Yeezz Beacon Scanner version %s', VERSION)
logger.debug('Memory allocated: ' + str(gc.mem_alloc()) + ' ,free: ' + str(gc.mem_free()))

# Set watchdog 5min
wdt = machine.WDT(timeout=300000)

try:

    # Start network
    logger.info('Start WLAN network [%s]', config.WLAN_SSID)
    network = WLANNetwork(ssid=config.WLAN_SSID, key=config.WLAN_KEY)
    network.connect()

    wdt.feed() # Feed

    # Sync correct time with NTP
    logger.info('Sync time with NTP')
    ntp = NTP(ntp_pool_server=config.NTP_POOL_SERVER)
    ntp.sync()

    wdt.feed() # Feed

    # Connect to AWS
    logger.info('Start connection AWS IoT')
    aws = AWS()
    aws.connect()

    wdt.feed() # Feed

    # Publish alive message
    logger.info('Publish device alive message')
    aliveMsg = AliveMessage(config.DEVICE_ID, config.APPLICATION_ID)
    aws.publish(aliveMsg.to_dict())

    wdt.feed() # Feed

    # Init UART gps
    uart = machine.UART(1, pins=(DEFAULT_TX_PIN, DEFAULT_RX_PIN), baudrate=9600)

    # Init I2C
    i2c = machine.I2C(0, machine.I2C.MASTER, baudrate=400000)

    while True:

        wdt.feed() # Feed

        # Start Beacon scanning for 2min

        # Read GPS coordinates
        gps = GPS(uart=uart)
        gps.update()

        # Read Environment values

        # Publish to AWS

except Exception as e:
    pycom.rgbled(config.LED_COLOR_ERROR)
    logger.error('Unexpected error [%s]', e)
