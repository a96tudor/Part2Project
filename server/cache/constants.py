"""
Part2Project -- constants.py

Copyright Apr 2018 [Tudor Mihai Avram]

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

DATABASE_SETUP = {
    "jobs": "CREATE TABLE jobs (" 
                "id SERIAL PRIMARY KEY, "
                "jobID VARCHAR(32) NOT NULL, "
                "status VARCHAR(10) NOT NULL, "
                "started DATE NOT NULL, "
                "stopped DATE"
            ")",

    "nodes": "CREATE TABLE nodes ("
                "id SERIAL PRIMARY KEY, "
                "uuid VARCHAR(50) NOT NULL, "
                "timemstmp INT NOT NULL, "
                "classifiedBy VARCHAR(50), "
                "validUntil DATE, "
                "showLikelihood FLOAT, "
                "hideLikelihood FLOAT, "
                "recommended VARCHAR(10) "
             ")",

    "jobsToNodes": "CREATE TABLE jobsToNodes ( "
                        "id SERIAL PRIMARY KEY, "
                        "jobID INT NOT NULL, "
                        "nodeID INT NOT NULL, "
                        "FOREIGN KEY (jobID) "
                            "REFERENCES jobs (id) "
                            "ON UPDATE CASCADE "
                            "ON DELETE CASCADE, "
                        "FOREIGN KEY (nodeID) "
                            "REFERENCES nodes (id) "
                            "ON UPDATE CASCADE "
                            "ON DELETE CASCADE"
                   ")"
}

SELECTS = {
    'jobID': 'SELECT jobs.id '
                'FROM jobs '
             'WHERE jobs.jobID=?',

    'node-cache-status': 'SELECT n.validUntil '
                            'FROM nodes AS n '
                            'WHERE n.uuid=? AND n.timestmp=?',

    'jobs-by-status': 'SELECT count(*) as count '
                        'FROM jobs '
                    'WHERE jobs.status=?',

    'nodes-for-job': 'SELECT n.uuid, n.timestmp, n.validUntil, n.showLikelihood, n.hideLikelihood, n.recommended '
                        'FROM nodes AS n '
                        'INNER JOIN jobsToNodes as jtn ON n.id=jtn.nodeID '
                        'INNER JOIN jobs as j ON jtn.jobID=j.id '
                     'WHERE j.jobID=?',

    'job-status': 'SELECT jobs.status '
                    'FROM jobs '
                  'WHERE jobs.jobID=?',

    'node-classification-results': 'SELECT nodes.showLikelihood, nodes.hideLikelihood, nodes.recommended '
                                        'FROM nodes '
                                   'WHERE nodes.uuid=? AND nodes.timestmp=?'
}

INSERT = {
    'new-job': 'INSERT INTO jobs(jobID, status, started) '
                    'VALUES (?, ?, ?)',

    'new-node': 'INSERT '
                'INTO nodes(uuid, timestmp, showLikelihood, hideLikelihood, recommended, classifiedBy, validUntil) '
                    'VALUES(?, ?, ?, ?, ?, ?, ?)',

    'node-to-job-rel': 'INSERT '
                       'INTO nodestojobs(jobID, nodeID) '
                            'VALUES(?, ?)'
}

