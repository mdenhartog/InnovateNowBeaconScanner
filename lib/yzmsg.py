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
# pylint: disable=R0913

"""
Yeezz Message module
"""
import json
import time

class Message(object):
    """
    Class for constructing a message to send
    """

    def __init__(self):
        """
        Initialize message
        """
        self.message = dict()

    def to_dict(self):
        """
        Transform the message to a dict
        """
        return self.message

    def to_json(self):
        """
        Transform the message to json
        """
        return json.dumps(self.message)


class GPSMessage(Message):
    """
    GPS message
    """
    def __init__(self, latitude=None, longitude=None, speed=None, course=None):

        super(GPSMessage, self).__init__()

        self.latitude = latitude
        self.longitude = longitude
        self.speed = speed
        self.course = course

    def to_dict(self):
        """
        Transform the message to a dict
        """
        self.message = super(GPSMessage, self).to_dict()

        self.message['sensor'] = 'GPS'

        if self.latitude:
            self.message['latitude'] = self.latitude

        if self.longitude:
            self.message['longitude'] = self.longitude

        if self.speed:
            self.message['speed'] = self.speed

        if self.course:
            self.message['course'] = self.course

        return self.message


class EnvironMessage(Message):
    """
    Environmental messge
    """
    def __init__(self, temperature=None, humidity=None, barometric_pressure=None, lux=None):

        super(EnvironMessage, self).__init__()

        self.temperature = temperature
        self.humidity = humidity
        self.barometric_pressure = barometric_pressure
        self.lux = lux

    def to_dict(self):
        """
        Transform the message to a dict
        """
        self.message = super(EnvironMessage, self).to_dict()

        self.message['sensor'] = 'Environment'

        if self.temperature:
            self.message['temperature'] = round(self.temperature, 2)

        if self.humidity:
            self.message['humidity'] = round(self.humidity, 0)

        if self.barometric_pressure:
            self.message['barometricPressure'] = round(self.barometric_pressure, 0)

        if self.lux:
            self.message['lux'] = round(self.lux, 0)

        return self.message

class AliveMessage(Message):
    """
    Alive message
    """
    def __init__(self, device_id=None, application_id=None):

        """
        Initialize Alive message
        """
        super(AliveMessage, self).__init__()

        self.device_id = device_id
        self.application_id = application_id

    def to_dict(self):
        """
        Transform the message to a dict
        """
        self.message = super(AliveMessage, self).to_dict()

        self.message['dev_id'] = self.device_id
        self.message['app_id'] = self.application_id
        self.message['time'] = time.time()

        return self.message

class AWSMessage(Message):
    """
    AWS message to send
    """

    def __init__(self, device_id=None, application_id=None, \
                 environ_message=None, gps_message=None, beacons=None, tags=None):
        """
        Initialize AWS message
        """
        super(AWSMessage, self).__init__()

        self.device_id = device_id
        self.application_id = application_id
        self.environ_message = environ_message
        self.gps_message = gps_message
        self.beacons = beacons
        self.tags = tags

    def to_dict(self):
        """
        Transform the message to a dict
        """
        self.message = super(AWSMessage, self).to_dict()

        self.message['dev_id'] = self.device_id
        self.message['app_id'] = self.application_id
        self.message['time'] = time.time()

        self.message['sensors'] = list()

        if self.environ_message:
            self.message['sensors'].append(self.environ_message)

        if self.gps_message:
            self.message['sensors'].append(self.gps_message)

        if self.beacons:
            self.message['beacons'] = self.beacons

        if self.tags:
            self.message['tags'] = self.tags

        return self.message
