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
             'WHERE jobs.jobID=%s',

    'node-cache-status': 'SELECT n.validUntil '
                            'FROM nodes AS n '
                            'WHERE n.uuid=%s AND n.timestmp=%d',

    'jobs-by-status': 'SELECT count(*) as count '
                        'FROM jobs '
                    'WHERE jobs.status=%s',

    'nodes-for-job': 'SELECT n.uuid, n.timestmp, n.validUntil, n.showLikelihood, n.hideLikelihood, n.recommended '
                        'FROM nodes AS n '
                        'INNER JOIN jobsToNodes as jtn ON n.id=jtn.nodeID '
                        'INNER JOIN jobs as j ON jtn.jobID=j.id '
                     'WHERE j.jobID=%s',

    'job-status': 'SELECT jobs.status '
                    'FROM jobs '
                  'WHERE jobs.jobID=%s',

    'node-classification-results': 'SELECT nodes.showLikelihood, nodes.hideLikelihood, nodes.recommended '
                                        'FROM nodes '
                                   'WHERE nodes.uuid=%s AND nodes.timestmp=%d',

    'running-jobs': 'SELECT jobs.jobID '
                        'FROM jobs '
                    'WHERE jobs.status="RUNNING"',

    'node-existance': 'SELECT count(*) AS count'
                'FROM nodes '
            'WHERE nodes.uuid=%s AND nodes.timestmp=%s',

    'nodeID': 'SELECT nodes.id '
              'FROM nodes '
              'WHERE nodes.uuid=%s AND nodes.timesmp=%s'
}

INSERTS = {
    'new-job': 'INSERT INTO jobs(jobID, status, started) '
                    'VALUES (%s, %s, now())',

    'new-node': 'INSERT '
                'INTO nodes(uuid, timestmp, showLikelihood, hideLikelihood, recommended, classifiedBy, validUntil) '
                    'VALUES(%s, %d, %f, %f, %s, %s, )',

    'node-to-job-rel': 'INSERT '
                       'INTO nodestojobs(jobID, nodeID) '
                            'VALUES(%s, %s)'
}

UPDATES = {
    'job-status': 'UPDATE jobs '
                    'SET jobs.status=%s '
                  'WHERE jobs.jobID=%s',

    'node-results': 'UPDATE nodes '
                        'SET nodes.showlikelihood=%s, '
                            'nodes.hidelikelihood=%s, '
                            'nodes.recommended=%s, '
                            'nodes.validuntil=%s '
                    'WHERE nodes.uuid=%s, nodes.timestmp=%s'
}

ACCEPTED_JOB_STATUS = ['WAITING', 'RUNNING', 'STOPPED', 'DONE']