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

    def _exists_node(self,
                 uuid: str,
                 timestamp: int):
        """

        :param uuid:            The unique ID of the node
        :param timestamp:       The timestamp of the node

        :return:                True - if it exists
                                False - otherwise
        """
        query = SELECTS['node-existance']

        result = self.postgresDriver.execute_SELECT(query, (uuid, timestamp, ))

        if result[0][0] != 0:
            # it's already in the cache db
            return True
        else:
            return False

    def _get_node_id(self,
                     uuid: str,
                     timestamp: int):
        """

        :param uuid:        Unique ID of the node
        :param timestamp:   Timestamp of the node

        :return:            the internal cache ID of the node - if exists & successful
                            None - otherwise
        """
        query = SELECTS['nodeID']

        try:
            results = self.postgresDriver.execute_SELECT(query, (uuid, timestamp, ))

            if len(results) == 0:
                return None

            return results[0][0]
        except:
            return None

    def _get_job_id(self,
                    jobID:str):
        """

        :param jobID:   Public job ID

        :return:        The internal job ID - if exists & successful
                        None - otherwise
        """
        query = SELECTS['jobID']

        try:
            results = self.postgresDriver.execute_SELECT(query, (jobID, ))

            if len(results) == 0:
                return None

            return results[0][0]
        except:
            return None

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

        :return:            The job status - if successful
                            None - if not successful
        """
        query = SELECTS['job-status']
        try:
            status = self.postgresDriver.execute_SELECT(query, jobID)[0][0]

            return status
        except:
            return None

    def add_node_results(self,
                     jobID: str,
                     uuid: str,
                     timestamp: int,
                     showProb: float,
                     hideProb: float,
                     recommended: str,
                     ttl: int,
                     override:bool=True):
        """

        :param jobID:                   The job the node belongs to
        :param uuid:                    The uuid of the node
        :param timestamp:               The timestamp of the node
        :param showProb:                Probability that the node should be shown
        :param hideProb:                Probability that the node should be hidden
        :param recommended:             Recommended action(i.e. 'SHOW' or 'HIDE')
        :param ttl:                     Time-to-live for this cached value
        :param override:                Whether to override the cache entry if the node
                                    was already entered or not

        :return:                        True - if successful
                                        False - otherwise
        """
        assert(recommended in ['SHOW', 'HIDE'])

        jobInnerID = self._get_job_id(jobID)

        if jobInnerID is None:
            # The jobID is not valid!! Therefore, fail!
            return False

        # First, checking if the node already exists in the database
        nodeInnerID = self._get_node_id(uuid, timestamp)

        if nodeInnerID is not None:

            query = INSERTS['node-to-job-rel']

            try:
                self.postgresDriver.execute_INSERT(query, (nodeInnerID, jobInnerID, ))
            except:
                # The insert failed, thus return False
                return False

            if not override:
                # All done
                return True

            # Otherwise, we need to update the database

            query = UPDATES['node-results']

            try:
                self.postgresDriver.execute_UPDATE(
                    query,
                    (showProb, hideProb, None, uuid, timestamp, )
                )

                return True
            except:
                # The update failed, so return False
                return False

        # If the node wasn't already in the database,
        # then we first need to add it as a new entry

        # TODO