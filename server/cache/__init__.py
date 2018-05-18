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
            results = self.postgresDriver.execute_SELECT(query, uuid, timestamp)

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

    def _node_clashes_with_job(self,
                               jobID: str,
                               innerNodeID: int):
        """

        :param jobID:
        :return:
        """

        query = SELECTS['inner-nodes-for-job']

        results = self.postgresDriver.execute_SELECT(
            query,
            jobID
        )

        if results is None or len(results) == 0:
            return False

        nodes = [x[0] for x in results]

        return innerNodeID in nodes

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
                    status: str='WAITING'):
        """

        :param jobID:               The ID of the job we're adding
        :param startedAt:           Datetime object with the
        :param status:              The initial status of the job. Default 'WAITING'.

        :return:                    True - if successful
                                    False - otherwise
        :raises AssertionError:     If the status provided is not one of WAITING, RUNNING, STOPPED or DONE
        """
        assert(status in ACCEPTED_JOB_STATUS)

        query = INSERTS['new-job']
        if startedAt is None:
            startedAt = dt.now()

        self.postgresDriver.execute_INSERT(
            query,
            jobID, status
        )
        return True

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


        query = UPDATES['job-status']
        self.postgresDriver.execute_UPDATE(
            query,
            newStatus, jobID
        )
        return True

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

        status = self.postgresDriver.execute_SELECT(query, jobID)

        if status is None or len(status) == 0:
            return None

        return status[0][0]

    def add_node_to_job_rel(self,
                            uuid: str,
                            timestamp: int,
                            jobID: str):
        """

        :param uuid:
        :param timestamp:
        :param jobID:
        :return:
        """

        nodeInnerID = self._get_node_id(uuid, timestamp)
        jobInnerID = self._get_job_id(jobID)

        if self._node_clashes_with_job(
            jobID=jobID,
            innerNodeID=nodeInnerID
        ):
            return

        query = INSERTS['node-to-job-rel']

        self.postgresDriver.execute_INSERT(
            query,
            jobInnerID, nodeInnerID
        )

    def add_node_results(self,
                     jobID: str,
                     uuid: str,
                     timestamp: int,
                     showProb: float,
                     hideProb: float,
                     recommended: str,
                     ttl: int=None,
                     override:bool=True,
                     classifiedbY:str='N/A'):
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
        :param classifiedbY:            The name of the classifier used by the node

        :return:                        True - if successful
                                        False - otherwise
        """
        assert(recommended in ['SHOW', 'HIDE'] or recommended is None)

        self.postgresDriver.reset_connection()

        jobInnerID = self._get_job_id(jobID)

        if jobInnerID is None:
            # The jobID is not valid!! Therefore, fail!
            return False

        # First, checking if the node already exists in the database
        nodeInnerID = self._get_node_id(uuid, timestamp)

        if nodeInnerID is not None:

            query = INSERTS['node-to-job-rel']

            try:
                self.postgresDriver.execute_INSERT(query,
                                                   jobInnerID, nodeInnerID)
            except:
                # The insert failed, thus return False
                return False

            if not override:
                # All done
                return True

            # Otherwise, we need to update the database

            query = UPDATES['node-results']

            self.postgresDriver.execute_UPDATE(
                query,
                showProb, hideProb, recommended, uuid, timestamp
            )

            try:


                return True
            except:
                # The update failed, so return False
                return False

        # If the node wasn't already in the database,
        # then we first need to add it as a new entry

        query = INSERTS['new-node']

        self.postgresDriver.execute_INSERT(
            query,
            uuid, timestamp, showProb, hideProb, recommended, classifiedbY
        )

        # Now getting the node ID
        nodeInnerID = self._get_node_id(uuid=uuid, timestamp=timestamp)

        query = INSERTS['node-to-job-rel']

        self.postgresDriver.execute_INSERT(
            query,
            jobInnerID, nodeInnerID
        )

        return True

    def cache_valid(self,
                   uuid: str,
                   timestamp: int):
        """
            Method that checks if the cache for one node is still valid or not.

        :param uuid:            The uuid of the node in question.
        :param timestamp:       The timestamp of the node in question.

        :return:                True - if the cache is still valid
                                False - otherwise
        """

        query = SELECTS['node-cache-status']

        status = self.postgresDriver.execute_SELECT(
            query,
            uuid, timestamp
        )

        if status is None or len(status) == 0:
            # The node is not in the database
            return False
        else:
            status = status[0][0]

            return status is None

    def get_node_cache_entry(self,
                             uuid: str,
                             timestamp: int):
        """

        :param uuid:
        :param timestamp:
        :return:
        """

        query = SELECTS['node-classification-results']

        results = self.postgresDriver.execute_SELECT(
            query,
            uuid, timestamp
        )

        return results

    def get_nodes_for_job(self,
                          jobID: str):
        """

        :param jobID:        The id of the job we extract the classification results for
        :return:             A dictionary with the following format:

                                {
                                    'status': <one of DONE, RUNNING or WAITING>
                                }

        """

        query = SELECTS['nodes-for-job']

        results = self.postgresDriver.execute_SELECT(
            query,
            jobID
        )

        status = self.get_job_status(jobID)

        if status is None:
            return None

        final_results = dict()
        final_results['status'] = status
        final_results['results'] = list()

        for result in results:
            final_results['results'].append({
                'uuid': result[0],
                'timestamp': result[1],
                'showProb': result[3],
                'hideProb': result[4],
                'recommended': result[5],
                'classifiedBy': result[6]
            })

        return final_results

    def clear_cache(self):
        """
            Method used to clear the cache database

        :return:        -
        """

        for table in TABLES:
            query = DELETE_CUSTOM % table

            self.postgresDriver.execute_DELETE(query)
