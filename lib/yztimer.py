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
# pylint: disable=E0401,R0903,R0201,C0103

"""
Yeezz timer module
"""
import sys
import logging

import machine

# Initialize logging
try:
    import config
    logging.basicConfig(level=config.LOG_LEVEL, stream=sys.stdout)
except ImportError:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

logger = logging.getLogger(__name__)

class Timer(object):
    """
    Timer class
    """
    def __init__(self, seconds=0, callback=None):
        """
        Init timer
        """
        self._alarm = machine.Timer.Alarm(callback, seconds, periodic=True)

class ResetTimer(Timer):
    """
    Reset the device after the timer expires
    """

    def __init__(self, seconds=0):
        """
        Init reset Timer
        """
        super(ResetTimer, self).__init__(self._reset_handler, seconds)

    def _reset_handler(self, alarm):
        """
        Reset the device
        """
        if alarm:
            logger.info("Resetting the device...")
            machine.reset()
