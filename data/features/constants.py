"""
Part2Project -- constants.py

Copyright Mar 2018 [Tudor Mihai Avram]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

FEATURES = [
    'NODE_TYPE',
    'NEIGH_TYPE',
    'EDGE_TYPE',
    'WEB_CONN',
    'NEIGH_WEB_CONN',
    'UID_STS',
    'GID_STS',
    'VERSION',
    'SUSPICIOUS',
    'EXTERNAL'
]

FEATURES_ONE_HOT = [
    'NODE_FILE',
    'NODE_PROCESS',
    'NODE_SOCKET',
    'NEIGH_FILE',
    'NEIGH_PROCESS',
    'NEIGH_SOCKET',
    'EDGE_PO_CLIENT',
    'EDGE_PO_SERVER',
    'EDGE_PO_RaW',
    'EDGE_PO_READ',
    'EDGE_PO_WRITE',
    'EDGE_PO_BIN',
    'EDGE_PO_NONE',
    'WEB_CONN',
    'NEIGH_WEB_CONN',
    'UID_STS',
    'GID_STS',
    'VERSION',
    'SUSPICIOUS',
    'EXTERNAL',
    'DEGREE',
    'NEIGH_DIST',
    'NEIGH_DEGREE'
]

ACCEPTED_NODES = [
    "File",
    "Socket",
    "Process"
]

NODE_TYPE_FEATURES = {
    'NODE_FILE': 'File',
    'NODE_PROCESS': 'Process',
    'NODE_SOCKET': 'Socket'
}

NEIGH_TYPE_FEATURES = {
    'NEIGH_FILE': 'FILE',
    'NEIGH_PROCESS': 'Process',
    'NEIGH_SOCKET': 'Socket'
}

EDGE_TYPE_FEATURES = {
    'EDGE_PO_CLIENT': 'CLIENT',
    'EDGE_PO_SERVER': 'SERVER',
    'EDGE_PO_RaW': 'RaW',
    'EDGE_PO_READ': 'READ',
    'EDGE_PO_WRITE': 'WRITE',
    'EDGE_PO_BIN': 'BIN',
    'EDGE_PO_NONE': 'NONE'
}

BLACKLIST = {
    'Process': [
        'sudo', 'chmod', 'usermod', 'groupmod', 'rm -rf',
        '/etc/pwd', '/usr/bin', '/usr/lib', '/bin/', '/lib',
        'attack', 'virus', 'worm', 'trojan'
    ],
    'File': [
        'attack', 'worm', 'virus', 'trojan'
    ]
}

DANGEROUS_LOCATIONS = [
    '/etc/pwd', '/usr/bin', '/usr/lib', '/bin/', '/lib', '/boot', '/dev', '/root'
]

LABELS = [
    'SHOW', 'HIDE'
]