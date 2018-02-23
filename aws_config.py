
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

"""
 InnovateNow Beacon Scanner AWS configuration settings
"""

from config import DEVICE_ID

# Host to connect to
AWS_IOT_HOST = "a3c6ugxemi0ejq.iot.eu-central-1.amazonaws.com"

# Port
AWS_IOT_PORT = 8883

# Topic to publish to
AWS_IOT_TOPIC = "beaconscanner"

# Certificate
AWS_IOT_CLIENT_CERT = "/flash/cert/certificate.pem.crt"

# Certificate private key file
AWS_IOT_PRIVATE_KEY = "/flash/cert/private.pem.key"

# Certificate root
AWS_IOT_ROOT_CA = "/flash/cert/aws-iot-rootCA.ca"

################## Subscribe / Publish client #################
AWS_IOT_CLIENT_ID = DEVICE_ID
AWS_IOT_OFFLINE_QUEUE_SIZE = -1
AWS_IOT_DRAINING_FREQ = 2
AWS_IOT_CONN_DISCONN_TIMEOUT = 30
AWS_IOT_MQTT_OPER_TIMEOUT = 10
AWS_IOT_LAST_WILL_TOPIC = 'lastwillmessage'
AWS_IOT_LAST_WILL_MSG = 'Last will of device [' + DEVICE_ID + ']'

####################### Shadow updater ########################
#THING_NAME = "my thing name"
#CLIENT_ID = "ShadowUpdater"
#CONN_DISCONN_TIMEOUT = 10
#MQTT_OPER_TIMEOUT = 5

####################### Delta Listener ########################
#THING_NAME = "my thing name"
#CLIENT_ID = "DeltaListener"
#CONN_DISCONN_TIMEOUT = 10
#MQTT_OPER_TIMEOUT = 5

####################### Shadow Echo ########################
#THING_NAME = "my thing name"
#CLIENT_ID = "ShadowEcho"
#CONN_DISCONN_TIMEOUT = 10
#MQTT_OPER_TIMEOUT = 5
