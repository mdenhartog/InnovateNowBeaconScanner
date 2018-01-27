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
# pylint: disable=E0401,E1101,W0703,C0411,C0103,E1205

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
---------------------------------------------
Next version items
---------------------------------------------
9. Retrieve messages from AWS Yeezz IoT Enviroment for this device
10. Check for OTA updates (once a day)
"""

import logging
import machine
import config
import pycom
import gc
import sys
import time

from version import VERSION
from yznetwork import WLANNetwork, NTP
from yzaws import AWS
from yzble import Scanner
from yzmsg import AliveMessage, GPSMessage, EnvironMessage, AWSMessage
from yzgps import GPS, DEFAULT_RX_PIN, DEFAULT_TX_PIN
from yzenvsensor import Environment

# Initialize logging
try:
    logging.basicConfig(level=config.LOG_LEVEL, stream=sys.stdout)
except ImportError:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

logger = logging.getLogger(__name__)

# Led orange
pycom.rgbled(config.LED_COLOR_WARNING)

logger.info('Start Yeezz Beacon Scanner version {}', VERSION)
logger.debug('Memory allocated: ' + str(gc.mem_alloc()) + ' ,free: ' + str(gc.mem_free()))

# Set watchdog 5min
wdt = machine.WDT(timeout=300000)

try:

    # Start network
    logger.info('Start WLAN network [{}]', config.WLAN_SSID)
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

    # Init scanner
    scanner = Scanner(max_list_items=50)

    # Init GPS
    gps = GPS(uart=uart)

    # Init environment sensors
    environ = Environment(i2c)

    # Led off
    pycom.heartbeat(False)

    while True:

        logger.debug('Memory allocated: ' + str(gc.mem_alloc()) + ' ,free: ' + str(gc.mem_free()))

        wdt.feed() # Feed

        # Start Beacon scanning for 2min
        scanner.start(timeout=config.SCAN_TIME_IN_SECONDS)
        scanner.stop()

        wdt.feed() # Feed

        # Read GPS coordinates
        gps.update()

        wdt.feed() # Feed

        # Construct messsages
        gps_msg = GPSMessage(latitude=gps.latitude,
                             longitude=gps.longitude,
                             altitude=gps.altitude,
                             speed=gps.speed(),
                             course=gps.course,
                             direction=gps.direction)

        env_msg = EnvironMessage(temperature=environ.temperature,
                                 humidity=environ.humidity,
                                 barometric_pressure=environ.barometric_pressure,
                                 lux=environ.lux)

        aws_msg = AWSMessage(device_id=config.DEVICE_ID,
                             application_id=config.APPLICATION_ID,
                             environ_message=env_msg.to_dict(),
                             gps_message=gps_msg.to_dict(),
                             beacons=scanner.beacons,
                             tags=scanner.tags)

        # Publish to AWS
        pycom.rgbled(config.LED_COLOR_OK) # Led green
        aws.publish(aws_msg.to_dict())
        pycom.heartbeat(False)

        wdt.feed() # Feed

        # Reset everything
        scanner.reset()

        gps_msg = None
        env_msg = None
        aws_msg = None

except Exception as e:
    pycom.rgbled(config.LED_COLOR_ERROR)
    logger.error('Unexpected error {}', e)

    time.sleep(5) # Wait for 5secs before reset
    machine.reset() # reset device
