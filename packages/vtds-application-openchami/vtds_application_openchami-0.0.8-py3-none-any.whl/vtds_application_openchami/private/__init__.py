#
# MIT License
#
# (C) Copyright 2025 Hewlett Packard Enterprise Development LP
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
"""Module initialization

"""

from os import sep as separator
from os.path import (
    join as path_join,
    dirname
)
CONFIG_DIR = path_join(dirname(__file__), "config")
TEMPLATE_DIR_PATH = path_join(
    dirname(__file__),
    'templates',
)


def template(filename):
    """Translate a file name into a full path name to a file in the
    scripts directory.

    """
    return path_join(TEMPLATE_DIR_PATH, filename)


def home(filename):
    """Translate a filename into a full path on a remote host that is
    in the 'root' home directory.

    """
    return path_join(separator, "root", filename)


# Templated files to be deployed to the managment node: (source, dest,
# mode, tag, run)
MANAGEMENT_NODE_FILES = [
    (
        template('magellan_discovery_dockerfile'),
        home('magellan_discovery_dockerfile'),
        '644',
        'magellan-discovery-dockerfile',
        False
    ),
    (
        template('magellan_discovery.sh'),
        home('magellan_discovery.sh'),
        '755',
        'magellan_discovery_script',
        False,
    ),
    (
        template('OpenCHAMI-Stage1-Deploy.sh'),
        home('OpenCHAMI-Stage1-Deploy.sh'),
        '755',
        'OpenCHAMI_Stage1_Deploy_script',
        False,
    ),
    (
        template('OpenCHAMI-Stage2-Deploy.sh'),
        home('OpenCHAMI-Stage2-Deploy.sh'),
        '755',
        'OpenCHAMI_Stage2_Deploy_script',
        False,
    ),
    (
        template('OpenCHAMI-Prepare.sh'),
        home('OpenCHAMI-Prepare.sh'),
        '755',
        'OpenCHAMI_Prepare_script',
        False,
    ),
    (
        template('OpenCHAMI-Remove.sh'),
        home('OpenCHAMI-Remove.sh'),
        '755',
        'OpenCHAMI_Remove_script',
        False,
    ),
    (
        template('OpenCHAMI-Logs.sh'),
        home('OpenCHAMI-Logs.sh'),
        '755',
        'OpenCHAMI_Logs_script',
        False,
    ),
    (
        template('OpenCHAMI-Show.sh'),
        home('OpenCHAMI-Show.sh'),
        '755',
        'OpenCHAMI_Show_script',
        False,
    ),
    (
        template('prepare_node.sh'),
        home('prepare_node.sh'),
        '755',
        'node_prepare_script',
        True,
    ),
]

# Templated files to be deployed to and run on the Virtual Blades
BLADE_FILES = [
    (
        template('nginx-default-site-config'),
        home('nginx-default-site-config'),
        '644',
        'nginx-default-site-config',
        False
    ),
    (
        template('sushy-emulator.conf'),
        home('sushy-emulator.conf'),
        '644',
        'sushy-emulator-configuration',
        False
    ),
    (
        template('sushy-emulator.service'),
        home('sushy-emulator.service'),
        '644',
        'sushy-emulator-unit-file',
        False
    ),
    (
        template('prepare_blade.sh'),
        home('prepare_blade.sh'),
        '700',
        'blade_prepare_script',
        True,
    ),
]
