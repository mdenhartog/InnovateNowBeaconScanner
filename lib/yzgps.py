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
# pylint: disable=R1702,C0103,E1101,E0401,W0703

"""
Yeezz GPS sensor based on serial GPS modules:
    - Tested with UBlox NEO-6M (9600 Baud, 8 bits, no parity bit, 1 stop bit)

Parsing of the NMEA sentences is done with the great micropyGPS library
"""
import logging
import sys
import time
from micropygps import MicropyGPS

# Initialize logging
try:
    import config
    logging.basicConfig(level=config.LOG_LEVEL, stream=sys.stdout)
except ImportError:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

logger = logging.getLogger(__name__)

DEFAULT_TX_PIN = 'P3'
DEFAULT_RX_PIN = 'P4'

# GPS_SEGMENTS = ['GPGSV', 'GPRMC', 'GPGSA', 'GPGGA', 'GPGLL', 'GPVTG']
GPS_SEGMENTS = ['GPRMC', 'GPGSA', 'GPGGA', 'GPGLL']

class GPS(object):
    """
    Class for getting the gps data via the serial bus.
    """

    def __init__(self, uart=None):
        """
        Initialize the GPS module on the specified portions
        """
        self.uart = uart
        self.parser = MicropyGPS(location_formatting='dd')
        self.is_running = False
        self.segments_parsed = []

    def update(self):
        """
        Update the GPS values
        """
        logger.info('Start reading the GPS values')
        self.is_running = True

        if self.uart:

            self.segments_parsed = []
            segments_found = False
            x = 0

            while not segments_found:

                logger.debug('GPS loop counter [' + str(x) + ']')
                if self.uart.any():

                    try:

                        read_bytes = self.uart.readall()
                        gps_string = read_bytes.decode("utf-8")
                        logger.debug('GPS [{}]', gps_string)

                        for c in gps_string:
                            segment = self.parser.update(str(c))
                            if segment:
                                logger.debug('Found segment [{}]', segment)
                                if segment not in self.segments_parsed:
                                    self.segments_parsed.append(segment)

                                    logger.debug('Parsed segments [{}]', self.segments_parsed)

                                    # GPGSV, GPRMC, GPGSA, gpGGA, GPGLL, GPVTG
                                    if all(i in self.segments_parsed for i in GPS_SEGMENTS):
                                        segments_found = True

                        x += 1
                        time.sleep(2) # Wait 2sec

                    except Exception as e:
                        logger.error('IOError [{}]', e)
                        break

        self.is_running = False

    @property
    def latitude(self):
        """
        Return latitude
        """
        return self.parser.latitude

    @property
    def longitude(self):
        """
        Return longitude
        """
        return self.parser.longitude

    @property
    def timestamp_utc(self):
        """ Return timestamp """
        return "20{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:.0f}Z".format(self.parser.date[2],
                                                                       self.parser.date[1],
                                                                       self.parser.date[0],
                                                                       self.parser.timestamp[0],
                                                                       self.parser.timestamp[1],
                                                                       self.parser.timestamp[2])

    def speed(self, unit='kph'):
        """
        Return speed
        @param unit: kph = Kilometer per hour
                     mph = Miles per hours
                     knot = Knots
        """

        if unit == 'mph':
            return self.parser.speed[1]

        if unit == 'knot':
            return self.parser.speed[0]

        return self.parser.speed[2]

    @property
    def altitude(self):
        """ Altitude """
        return self.parser.altitude

    @property
    def course(self):
        """ Actual course """
        return self.parser.course

    @property
    def direction(self):
        """ Direction """
        return self.parser.compass_direction()
