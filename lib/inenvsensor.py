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
# pylint: disable=C0103,E0401,R1710

"""
InnovateNow Environment Sensor based on:
    - BME280 sensor for Temperature, Humidity and Barometric pressure
"""
import bme280

# Initialize logging
import inlogging as logging
log = logging.getLogger(__name__)

class Environment(object):
    """
    Class for getting the Enviroment sensor values
    """

    def __init__(self, i2c=None):
        """
        Initialize the enviromental sensor
        """
        self.i2c = i2c

        if self.i2c:
            self.addresses = self.i2c.scan()

            # log.info('I2C addresses [{}]', self.addresses)
            log.info('BME280 [{}]', bme280.BME280_I2CADDR)

            self.bme280 = None
            if bme280.BME280_I2CADDR in self.addresses:
                log.info('Initialize Temperature, Humidity and Barometric sensor')
                self.bme280 = bme280.BME280(address=bme280.BME280_I2CADDR,
                                            i2c=i2c) # default address 0x76

    @property
    def temperature(self):
        """Return the current temperature in celsius"""
        if self.bme280:
            return self.bme280.temperature

    @property
    def humidity(self):
        """Return the current humidity percentage"""
        if self.bme280:
            return self.bme280.humidity

    @property
    def barometric_pressure(self):
        """Return the current barometric pressure in hPa"""
        if self.bme280:
            return self.bme280.pressure
