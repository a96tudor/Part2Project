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
    'EXTERNAL',
    'LABEL'
]

NODE_EDGE_CODES = {
    'Process': {
        'code': 1,
        'BIN': 1,
        'CLIENT': 2,
        'SERVER': 3,
        'RaW': 4
    },
    'File': {
        'code': 2,
        'BIN': 1
    },
    'Socket': {
        'code': 3,
        'CLIENT': 1,
        'SERVER': 2,
        'RaW': 3
    }
}

RULES = {
    'File': [
        'rule1',
        'rule4'
    ],
    'Process': {
        'File': [
            'rule5',
            'rule8',
            'rule9',
            'rule10',
            'rule14',
            'rule15'
        ],
        'Socket': [
            'rule2'
        ],
    },
    'Socket': [
        'rule3',
        'rule7'
    ]
}
