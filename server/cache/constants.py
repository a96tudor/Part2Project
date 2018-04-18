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
                "id INT PRIMARY KEY AUTOINCREMENT, "
                "jobID VARCHAR(32) NOT NULL, "
                "status VARCHAR(10) NOT NULL, "
                "started DATE NOT NULL, "
                "stopped DATE"
            ")",

    "nodes": "CREATE TABLE nodes ("
                "id INT PRIMARY KEY AUTOINCREMENT, "
                "uuid VARCHAR(50) NOT NULL, "
                "timemstmp INT NOT NULL, "
                "classifiedBy VARCHAR(50), "
                "validUntil DATE, "
                "showLikelihood FLOAT, "
                "hideLikelihood FLOAT, "
                "recommended VARCHAR(10) "
             ")",

    "jobsToNodes": "CREATE TABLE jobsToNodes ( "
                        "id INT PRIMARY KEY AUTOINCREMENT, "
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
