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
# pylint: disable=R1702,C0103

"""
Yeezz GPS sensor based on serial GPS modules:
    - Tested with UBlox NEO-6M (9600 Baud, 8 bits, no parity bit, 1 stop bit)

Parsing of the NMEA sentences is done with the great micropyGPS library
"""
import logging
from micropygps import MicropyGPS

# Initialize logging
try:
    import config
    logging.basicConfig(level=config.LOG_LEVEL)
except ImportError:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

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
        self.stop_requested = False
        self.segments_parsed = []

    def start(self):
        """
        Start reading the GPS values
        """
        logger.info('Start reading the GPS values')
        self.is_running = True

        if self.uart:
            while not self.stop_requested:

                if self.uart.any():

                    try:
                        read_bytes = self.uart.readall()
                        for c in read_bytes:
                            segment = self.parser.update(c)
                            if segment:
                                logger.info('Found segment [%s]', segment)
                                if segment not in self.segments_parsed:
                                    self.segments_parsed.append(segment)
                    except IOError as e:
                        logger.error('IOError [%s]', e)
                        break



    def stop(self):
        """
        Stop processing GPS values
        """
        logger.info('Stop reading the GPS values')
        self.stop_requested = True

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

    @property
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
    def course(self):
        """ Actual course """
        return self.parser.compass_direction()
