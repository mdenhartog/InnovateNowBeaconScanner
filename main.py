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
InnovateNow Beacon Scanner program

Steps
--------------------------------------------
1. Connect to Wifi
2. Get time from NTP Server
3. Connect to AWS Yeezz IoT environment
4. Send alive signal
5. Scan for Beacons / Tags for the specified amount of time
6. Initialize GPS
7. Initialize Environment sensor
8. Send message to AWS InnovateNow Environment
---------------------------------------------
Next version items
---------------------------------------------
9. Retrieve messages from AWS IoT Environment for this device
10. Check for OTA updates (once a day)
"""

import machine
import config
import pycom
import gc
import sys
import time

from version import VERSION
from innetwork import WLANNetwork, NTP
from inaws import AWS
from inble import BLEScanner
from inmsg import AliveMessage, GPSMessage, EnvironMessage, AWSMessage
from ingps import GPS
from inenvsensor import Environment
from intimer import ResetTimer

# Initialize logging
import inlogging as logging
try:
    logging.basicConfig(level=config.LOG_LEVEL, stream=sys.stdout)
except ImportError:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

log = logging.getLogger(__name__)

# Led orange
pycom.heartbeat(False)
pycom.rgbled(config.LED_COLOR_WARNING)

log.info('Start InnovateNow Beacon Scanner version {}', VERSION)
log.debug('Memory allocated: ' + str(gc.mem_alloc()) + ' ,free: ' + str(gc.mem_free()))

# Set watchdog 5min
wdt = machine.WDT(timeout=300000)

# Start device reset timer
if config.DEVICE_RESET_AFTER_SECONDS:
    reset_timer = ResetTimer(config.DEVICE_RESET_AFTER_SECONDS)

try:

    # Start network
    log.info('Start WLAN network [{}]', config.WLAN_SSID)
    network = WLANNetwork(ssid=config.WLAN_SSID, key=config.WLAN_KEY)
    network.connect()

    wdt.feed() # Feed

    # Sync correct time with NTP
    log.info('Sync time with NTP')
    ntp = NTP(ntp_pool_server=config.NTP_POOL_SERVER)
    ntp.sync()

    wdt.feed() # Feed

    # Connect to AWS
    log.info('Start connection AWS IoT')
    aws = AWS()
    aws.connect()

    wdt.feed() # Feed

    # Publish alive message
    log.info('Publish device alive message')
    aliveMsg = AliveMessage(customer=config.CUSTOMER, device_id=config.DEVICE_ID)
    aws.publish(aliveMsg.to_dict())

    wdt.feed() # Feed

    # Init gps
    gps = None
    i2c = None
    if config.GPS_AVAILABLE and config.GPS_PORT == 'UART':
        log.info('Initialize GPS via Serial')
        uart = machine.UART(1, pins=(config.GPS_UART_TX_PIN, config.GPS_UART_RX_PIN), baudrate=9600)
        gps = GPS(uart=uart)

    if config.GPS_AVAILABLE and config.GPS_PORT == 'I2C':
        log.info('Initialize GPS via I2C on bus ' +
                 str(config.SENSOR_I2C_BUS) + ' and pins (' + config.SENSOR_I2C_SDA_PIN +
                 ',' + config.SENSOR_I2C_SCL_PIN + ')')

        if not i2c:
            i2c = machine.I2C(config.SENSOR_I2C_BUS,
                              machine.I2C.MASTER,
                              pins=(config.SENSOR_I2C_SDA_PIN, config.SENSOR_I2C_SCL_PIN))
            log.info('I2C addresses available [{}]', i2c.scan())
        gps = GPS(i2c=i2c)

    # Init environmental sensors
    if config.ENVIRONMENT_SENSOR_AVAILABLE:
        log.info('Initialize Environmental sensor via I2C via bus ' +
                 str(config.SENSOR_I2C_BUS) + ' and pins (' + config.SENSOR_I2C_SDA_PIN +
                 ',' + config.SENSOR_I2C_SCL_PIN + ')')

        if not i2c:
            i2c = machine.I2C(config.SENSOR_I2C_BUS,
                              machine.I2C.MASTER,
                              pins=(config.SENSOR_I2C_SDA_PIN, config.SENSOR_I2C_SCL_PIN))
            log.info('I2C addresses available [{}]', i2c.scan())

        environ = Environment(i2c=i2c)

    # Init scanner
    scanner = BLEScanner(max_list_items=50)

    # Led off
    pycom.heartbeat(False)

    while True:

        log.debug('Memory allocated: ' + str(gc.mem_alloc()) + ' ,free: ' + str(gc.mem_free()))

        wdt.feed() # Feed

        # Start Beacon scanning for 2min
        scanner.start(timeout=config.SCAN_TIME_IN_SECONDS)
        scanner.stop()

        wdt.feed() # Feed

        # Read GPS coordinates
        if config.GPS_AVAILABLE:
            gps.update()

        wdt.feed() # Feed

        # Construct messsages
        gps_msg = GPSMessage()
        if config.GPS_AVAILABLE:
            gps_msg = GPSMessage(id=config.GPS_SENSOR_ID,
                                 latitude=gps.latitude[0],
                                 longitude=gps.longitude[0],
                                 altitude=gps.altitude,
                                 speed=gps.speed(),
                                 course=gps.course,
                                 direction=gps.direction)
        else:
            gps_msg = GPSMessage(latitude=config.GPS_FIXED_LATITUDE,
                                 longitude=config.GPS_FIXED_LONGITUDE)

        env_msg = EnvironMessage()
        if config.ENVIRONMENT_SENSOR_AVAILABLE:
            env_msg = EnvironMessage(id=config.ENVIRONMENT_SENSOR_ID,
                                     temperature=environ.temperature,
                                     humidity=environ.humidity,
                                     barometric_pressure=environ.barometric_pressure)

        aws_msg = AWSMessage(customer=config.CUSTOMER,
                             device_id=config.DEVICE_ID,
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

        # Free up space
        if gc.mem_free() < 30000:
            gc.collect()

except Exception as e:
    pycom.rgbled(config.LED_COLOR_ERROR)
    log.error('Unexpected error {}', e)

    if aws:
        aws.disconnect()

    time.sleep(5) # Wait for 5secs before reset
    machine.reset() # Reset device
