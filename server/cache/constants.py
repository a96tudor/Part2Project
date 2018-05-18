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
                "status VARCHAR(100) NOT NULL, "
                "started DATE NOT NULL, "
                "stopped DATE"
            ")",

    "nodes": "CREATE TABLE nodes ("
                "id SERIAL PRIMARY KEY, "
                "uuid VARCHAR(100) NOT NULL, "
                "timemstmp BIGINT NOT NULL, "
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

    'node-cache-status': 'SELECT validuntil '
                            'FROM nodes '
                        'WHERE uuid=%s AND timemstmp=%s',

    'jobs-by-status': 'SELECT count(*) as count '
                        'FROM jobs '
                    'WHERE jobs.status=%s',

    'nodes-for-job': 'SELECT n.uuid, n.timemstmp, n.validuntil, n.showlikelihood, n.hidelikelihood, n.recommended, n.classifiedby '
                        'FROM nodes AS n '
                        'INNER JOIN jobsToNodes as jtn ON n.id=jtn.nodeid '
                        'INNER JOIN jobs as j ON jtn.jobid=j.id '
                     'WHERE j.jobid=%s',

    'job-status': 'SELECT jobs.status '
                    'FROM jobs '
                  'WHERE jobs.jobID=%s',

    'node-classification-results': 'SELECT nodes.showlikelihood, nodes.hidelikelihood, nodes.recommended, nodes.classifiedby '
                                        'FROM nodes '
                                   'WHERE nodes.uuid=%s AND nodes.timemstmp=%s '
                                   'LIMIT 1',

    'running-jobs': 'SELECT jobs.jobid '
                        'FROM jobs '
                    'WHERE jobs.status="RUNNING"',

    'node-existance': 'SELECT count(*) AS count '
                'FROM nodes '
            'WHERE nodes.uuid=%s AND nodes.timestmp=%s',

    'nodeID': 'SELECT nodes.id '
              'FROM nodes '
              'WHERE nodes.uuid=%s AND nodes.timemstmp=%s',

    'inner-nodes-for-job': 'SELECT jtn.nodeid '
                            'FROM jobstonodes AS jtn '
                            'INNER JOIN jobs AS j '
                                'ON jtn.jobid=j.id '
                           'WHERE j.jobid=%s'
}

INSERTS = {
    'new-job': 'INSERT INTO jobs(jobID, status, started) '
                    'VALUES (%s, %s, now())',

    'new-node': 'INSERT '
                'INTO nodes(uuid, timemstmp, showlikelihood, hidelikelihood, recommended, classifiedby) '
                    'VALUES(%s, %s, %s, %s, %s, %s)',

    'node-to-job-rel': 'INSERT '
                       'INTO jobstonodes(jobid, nodeid) '
                            'VALUES(%s, %s)'
}

UPDATES = {
    'job-status': "UPDATE jobs "
                    "SET status='%s' "
                  "WHERE jobid='%s'",

    'node-results': 'UPDATE nodes '
                        'SET showlikelihood=%f, '
                            'hidelikelihood=%f, '
                            "recommended='%s' "
                    "WHERE uuid='%s' AND timemstmp=%s"
}

ACCEPTED_JOB_STATUS = ['WAITING', 'RUNNING', 'STOPPED', 'DONE']