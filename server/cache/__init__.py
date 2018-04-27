"""
Part2Project -- __init__.py

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
from datetime import datetime as dt
from numpy import random

from server.cache.driver import PostgresDriver
from server.cache.constants import *
from exceptions.server import *


class CacheHandler(object):
    """

    """
    def __init__(self,
                 dbName: str,
                 host: str,
                 user: str,
                 password: str,
                 port: int):
        """

        :param dbName:
        :param host:
        :param user:
        :param password:
        :param port:
        """
        self.postgresDriver = PostgresDriver(
            host=host,
            port=port,
            user=user,
            password=password,
            dbName=dbName
        )

    def _generate_jobID(self):
        """
            Private method generating a new jobID

        :return:        The resulting jobID
        """
        current_date = str(dt.now()).replace(' ', '').replace('-', '').replace('.', '').replace(':', '')
        rnd_seq = ''.join(
            [str(x) for x in random.choice(9,5)]
        )

    def get_running_jobs(self):
        """
            Method that gets all the running jobs according to the database

        :return:    A list of running jobs
        """
        try:
            query = SELECTS['running-jobs']
            jobs = self.postgresDriver.execute_SELECT(query)
            return jobs
        except:
            return None

    def add_new_job(self,
                    jobID: str,
                    startedAt=None,
                    status:str='WAITING'):
        """

        :param jobID:               The ID of the job we're adding
        :param startedAt:           Datetime object with the
        :param status:              The initial status of the job. Default 'WAITING'.

        :return:                    True - if successful
                                    False - otherwise
        :raises AssertionError:     If the status provided is not one of WAITING, RUNNING, STOPPED or DONE
        """
        assert(status in ACCEPTED_JOB_STATUS)

        try:
            query = INSERTS['new-job']
            if startedAt is None:
                startedAt = dt.now()

            self.postgresDriver.execute_INSERT(
                query,
                (jobID, startedAt, status, )
            )
            return True
        except:
            return False

    def update_job_status(self,
                          jobID: str,
                          newStatus: str):
        """"

        :param jobID:                The public job ID for which we perform the update
        :param newStatus:              The new status of the job

        :return:                    True - if successful
                                    False - otherwise
        :raises AssertionError:     If the status provided is not one of WAITING, RUNNING, STOPPED or DONE
        """
        assert(newStatus in ACCEPTED_JOB_STATUS)

        try:
            query = UPDATES['job-status']
            self.postgresDriver.execute_UPDATE(
                query,
                (jobID, newStatus, )
            )
            return True
        except:
            return False

    def stop_job(self,
                 jobID:str):
        """
                Method that changes the a job's status to 'STOPPED'

        :param jobID:       The public ID of the job we want to update the status for

        :return:            True - if successful
                            False - otherwise
        """
        return self.update_job_status(jobID, 'STOPPED')

    def mark_job_as_done(self,
                         jobID:str):
        """
                Method that updates a job's status to 'DONE'

        :param jobID:       The public ID of the job

        :return:            True - if successful
                            False - otherwise
        """
        return self.update_job_status(jobID, 'DONE')

    def get_job_status(self,
                       jobID:str):
        """
            Method that returns the cached status of a job

        :param jobID:       The public job ID

        :return:            The job status
        """
        
