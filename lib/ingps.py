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
# pylint: disable=R1702,C0103,E1101,E0401,W0703,W0102

"""
InnovateNow GPS sensor based on serial or I2C GPS modules with NMEA support.
Parsing of the NMEA sentences is done with the micropyGPS library.

Tested with:
- UBlox NEO-6M
- Quectel L76-L

pylint:
"""
import time
from machine import Timer
from micropygps import MicropyGPS

# Initialize logging
import inlogging as logging
log = logging.getLogger(__name__)

# Quectel L76-L address
GPS_I2CADDR = 0x10

SUPPORTED_GPS_SEGMENTS = ['GPGSV', 'GPRMC', 'GPGSA', 'GPGGA', 'GPGLL', 'GPVTG']

class DataReader(object):
    """
    Class for reading the gps data via uart
    """
    def __init__(self):
        self.__finished = False
        self.data = ''
        self.segments_parsed = []

    def start(self, i2c=None, uart=None, timeout=5, gps_segments=SUPPORTED_GPS_SEGMENTS):
        """
        Start reading GPS data
        """
        log.debug('Start reading the data')

        self.segments_parsed = []
        self.__finished = False

        """
        Write 1 byte to register to start sending data
        """
        if i2c:
            log.debug('Wake up GPS device')
            i2c.writeto(GPS_I2CADDR, self.data)

        Timer.Alarm(handler=self.__stop, s=timeout)
        while not self.__finished:
            ret_data = None

            if i2c:
                ret_data = self.__i2c_read_data(i2c)
            if uart:
                ret_data = self.__uart_read_data(uart)

            # Process the data read
            if ret_data:
                data_str = ret_data.decode("utf-8")
                data_array = data_str.split('$')

                log.debug('Read data: ' + str(data_array))

                # Process the data item
                for data_item in data_array:
                    # Add $ and remove \r\n
                    data_item = '$' + data_item.rstrip('\r\n')

                    log.debug('Process [' + data_item + ']')
                    if data_item.find('$GP') > -1 and data_item.find('*') > -1:

                        # Get segment and check if it has been already seen
                        segment = data_item.split(',')[0].lstrip('$')
                        log.debug('Segment [' + segment + '] found')

                        if not segment in self.segments_parsed:
                            self.segments_parsed.append(segment)
                            self.data = self.data + data_item

                        if all(i in self.segments_parsed for i in gps_segments):
                            self.__finished = True
                        else:
                            time.sleep_ms(2)

    def __uart_read_data(self, uart):
        """
        Read the data via UART
        """
        return uart.readall()

    def __i2c_read_data(self, i2c):
        """
        Read the data via i2c (255 bytes)
        """
        return i2c.readfrom(GPS_I2CADDR, 255)

    def __stop(self, alarm):
        if alarm:
            log.debug('Data reader timeout')
            self.__finished = True


class GPS(object):
    """
    Class for retrieving and processing the GPS data
    """

    def __init__(self, i2c=None, uart=None, timeout=5, gps_segments=SUPPORTED_GPS_SEGMENTS):
        """
        Initialize the GPS module on the specified portions
        """
        self.__uart = uart
        self.__i2c = i2c
        self.__parser = MicropyGPS(location_formatting='dd')
        self.is_running = False
        self.coords_valid = False    # Coordinates found
        self.is_valid = False        # All segments found
        self.__timeout = timeout     # Data reader timeout in seconds
        self.__gps_segments = gps_segments

    def update(self):
        """
        Update the GPS values
        """
        log.info('Start reading the GPS values')
        self.is_running = True

        datareader = DataReader()
        datareader.start(i2c=self.__i2c, uart=self.__uart, timeout=self.__timeout,
                         gps_segments=self.__gps_segments)

        self.coords_valid = False
        if all(i in datareader.segments_parsed for i in self.__gps_segments):
            self.is_valid = True

        for c in datareader.data:
            self.__parser.update(str(c))

        # Check if we found coords
        if self.__parser.latitude[0] != 0 and \
           self.__parser.longitude[0] != 0:
            log.debug('Found coordinates')
            self.coords_valid = True

        self.is_running = False

    @property
    def latitude(self):
        """
        Return latitude
        """
        return self.__parser.latitude

    @property
    def longitude(self):
        """
        Return longitude
        """
        return self.__parser.longitude

    @property
    def timestamp_utc(self):
        """ Return timestamp """
        return "20{0}-{1:02d}-{2:02d}T{3:02d}:{4:02d}:{5:.0f}Z".format(self.__parser.date[2],
                                                                       self.__parser.date[1],
                                                                       self.__parser.date[0],
                                                                       self.__parser.timestamp[0],
                                                                       self.__parser.timestamp[1],
                                                                       self.__parser.timestamp[2])

    def speed(self, unit='kph'):
        """
        Return speed
        @param unit: kph = Kilometer per hour
                     mph = Miles per hours
                     knot = Knots
        """

        if unit == 'mph':
            return self.__parser.speed[1]

        if unit == 'knot':
            return self.__parser.speed[0]

        return self.__parser.speed[2]

    @property
    def altitude(self):
        """ Altitude """
        return self.__parser.altitude

    @property
    def course(self):
        """ Actual course """
        return self.__parser.course

    @property
    def direction(self):
        """ Direction """
        return self.__parser.compass_direction()
