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

"""
InnovateNow AWS library
"""
import json
import sys
import socket

import aws_config as awsconfig
from MQTTLib import AWSIoTMQTTClient

# Initialize logging
import inlogging as logging
log = logging.getLogger(__name__)

class AWS(object):
    """
    AWS IoT communication with Pycom provided libraries
    """

    def __init__(self):
        """
        Initialization of AWS Class
        """
        self.client = None
        self.is_connected = False

    def connect(self):
        """
        Connect AWS IoT
        """

        if self.client is None:
            # Configure the MQTT client
            self.client = AWSIoTMQTTClient(awsconfig.AWS_IOT_CLIENT_ID)
            self.client.configureEndpoint(awsconfig.AWS_IOT_HOST, awsconfig.AWS_IOT_PORT)
            self.client.configureCredentials(awsconfig.AWS_IOT_ROOT_CA,
                                             awsconfig.AWS_IOT_PRIVATE_KEY,
                                             awsconfig.AWS_IOT_CLIENT_CERT)

            self.client.configureOfflinePublishQueueing(awsconfig.AWS_IOT_OFFLINE_QUEUE_SIZE)
            self.client.configureDrainingFrequency(awsconfig.AWS_IOT_DRAINING_FREQ)
            self.client.configureConnectDisconnectTimeout(awsconfig.AWS_IOT_CONN_DISCONN_TIMEOUT)
            self.client.configureMQTTOperationTimeout(awsconfig.AWS_IOT_MQTT_OPER_TIMEOUT)

        # Connect to MQTT Host
        if self.client.connect():
            self.is_connected = True
            log.info('AWS IoT connection succeeded')
        else:
            raise socket.error('AWS IoT connection failed')

    def publish(self, msg=None):
        """
        Publish message
        """
        log.info('Publish [{}]', json.dumps(msg))
        self.client.publish(awsconfig.AWS_IOT_TOPIC, json.dumps(msg), 1)

    def disconnect(self):
        """
        Disconnect AWS IoT
        """
        if self.client:
            if self.client.disconnect():
                log.info('AWS IoT disconnected')
                self.is_connected = False
                self.client = None
