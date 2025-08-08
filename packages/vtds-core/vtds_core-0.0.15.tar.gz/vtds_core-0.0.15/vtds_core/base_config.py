#
# MIT License
#
# (C) Copyright [2024] Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Public API for the layer base configuration data, this gives
callers access to the BaseConfig API and prevents them from seeing the
private implementation of the API or accessing the base configuration
files directly..

"""

from .private.config import PrivateBaseConfig


class BaseConfig:
    """BaseConfig class presents operations on the base configuration
    of the layer to callers.

    """
    def __init__(self):
        """Constructor

        """
        self.private = PrivateBaseConfig()

    def get_base_config(self):
        """Retrieve the base configuration for the layer in the
        form of a python data structure for use in composing and
        overall vTDS configuration.

        """
        return self.private.get_base_config()

    def get_base_config_text(self):
        """Retrieve the text of the base configuration file as a text
        string (UTF-8 encoded) for use in displaying the configuration
        to users.

        """
        return self.private.get_base_config_text()

    def get_test_overlay(self):
        """Retrieve a pre-defined test overlay configuration in the
        form of a python data structure for use in composing vTDS
        configurations for testing with this layer.

        """
        return self.private.get_test_overlay()
