FEATURES = [
    'UUID',
    'TIMESTAMP',
    'NODE_TYPE',
    'NEIGH_TYPE',
    'EDGE_TYPE',
    'WEB_CONN',
    'NEIGH_WEB_CONN',
    'UID_STS',
    'GID_STS',
    'VERSION',
    'SUSPICIOUS',
    'EXTERNAL',
    'LABEL'
]

NODE_EDGE_CODES = {
    'Process': {
        'code': 1,
        'BIN': 1,
        'CLIENT': 2,
        'SERVER': 3,
        'RaW': 4,
        'WRITE': 5,
        'NONE': 4,
        'READ': 6
    },
    'File': {
        'code': 2,
        'BIN': 1,
        'READ': 2,
        'WRITE': 2,
        'RaW': 2,
        'NONE': 2
    },
    'Socket': {
        'code': 3,
        'CLIENT': 1,
        'SERVER': 2,
        'RaW': 3
    }
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
