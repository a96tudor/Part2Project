"""
Part2Project -- views.py

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
from flask.views import View
from flask import request, Response
from server.utils import *
from server.jobs import JobsHandler


class ClassifyView(View):
    """
        Class representing the general entry point for the API.

        Path: /classify
        Methods: POST

        Is expecting a POST request containing a JSON with the following format:
                {
                    'nodes': [
                        {
                            'uuid': <unique id of the node>,
                            'timestamp': <timestamp of the node>
                        },
                        ...
                        {
                            'uuid': <unique id of the node>,
                            'timestamp': <timestamp of the node>
                        }
                    ]
                }

        It returns a JSON with the following format:
                {
                    'jobID': <The ID of the job initiated>,
                    'model': <The machine learning model used to classify the nodes>,
                    'caching_active': <True/ False>,
                    'nodes_to_process': <Number of nodes the job will work on>,
                    'started': <Timestamp of when the job was started>
                }
    """
    methods = ['POST']

    expected_values = ['uuid', 'timestamp']

    def validate_input(self):
        """

        :return:        - True if the incoming request is valid
                        - False otherwise
        """
        if request.method not in self.methods:
            return False, 'Invalid method. Expected POST, got %s' % request.method

        if not request.is_json:
            return False, 'Invalid data format. Expected JSON'

        data = request.json

        if not isinstance(data, dict):
           return False, 'Invalid datatype inside JSON. Expected dict, got %s' % str(type(data))

        if not (len(data) == 1 and 'nodes' in data):
            return False, 'Invalid data!'

        for entry in data['nodes']:
            if not isinstance(entry, dict):
                return False, 'Invalid datatype in nodes list. Expected dict, got %s.' % str(type(entry))
            for e in self.expected_values:
                if e not in entry:
                    return False, 'Invalid nodes list entry. Expected key %s not found.' % str(type(e))

        return True, 'Success'

    def generate_job(self,
                     nodes):
        """
            Method that generates a new job, runs it on a different process and returns the
            corresponding jobID

        :param nodes:       The nodes for the nodes to process
        :return:            The ID of the new job
        """
        jobID = jobsHandler.add_job(nodes)
        return jobID

    def dispatch_request(self):
        sts, msg = self.validate_input()

        if not sts:
            return Response(
                status=400,
                response=msg
            )

        if not isinstance(jobsHandler, JobsHandler):
            return Response(
                status=500,
                response='Internal error'
            )

        self.generate_job(request.json)

        return Response(200)


class Neo4JConnectView(View):
    """
        View handling the neo4j connection entry point to the API. It can be used by the client
        to change the database used in classification.

        Path: /db-connect
        Methods: PUT

        It expects the following JSON as data:
            {
                ‘host’:  <the ip/ url of the database’s host>,
			    ‘port’: <port # where to connect to the database>,
			    ‘user’: <username used to connect to the database>,
			    ‘pass’: <password used to connect to the database>,
			    'invalidate-cache': <True/ False - whether we have to invalidate the cache
			                                       when connecting to a new database>,
			    'forced': <True/ False - if set to True, then the API will force stop any
			                            job working on the old database before resetting
			                            the connection number>
            }

    """

    methods = ['PUT']
    keys = ['host', 'port', 'user', 'pass', 'invalidate-cache', 'forced']

    def validate_input(self):
        """
            Method that validates the input to the view

        :return:    True - if the input is valid
                    False - otherwise
        """
        if request.method not in self.methods:
            return False, 'Invalid method. Expected PUT, got %s' % request.method

        if not request.is_json:
            return False, 'Invalid data format. Expected JSON.'

        data = request.json

        if not isinstance(data, dict):
            return False, 'Invalid data type inside JSON. Expected dict, got %s' % str(type(data))

        for key in self.keys:
            if key not in data:
                return False, 'Invalid dictionary received. Key %s not found.' % key

        return True, 'Success'

    def dispatch_request(self):

        sts, msg = self.validate_input()

        if not sts:
            return Response(
                status=400,
                response=msg
            )

        data = request.json

        if jobsHandler.jobsRunning():
            if not data['forced']:
                return Response(
                    status=400,
                    response='ERROR: Job still working on the old database!'
                )
            else:
                print("Stopping running jobs!")

        # TODO: finish implementation

        return Response(200)


class JobActionView(View):
    """
        View handling any requests regarding job actions. At the moment,
        it handles the following:
            - returning job status
            - returning job partial/ total results
            - stopping a job

        Path: /job-action?id=<jobID>&action=<action>
        Methods: GET

        The action parameter will get one of the values: 'status', 'results', 'stop'

        If successful, it returns a JSON. Based on the 'action param', the JSON can have one of 3 formats:

            (1) action == 'status'
                {
                    'id':                   <the job id>,
                    'status':               <the status of the job. One of: 'WAITING', 'RUNNING', 'DONE', 'STOPPED'>,
                    'ran_for':              <how long the job ran for. in milliseconds>
                }

            (2) action == 'results'
                {
                    'id':                   <the job id>,
                    'job_status':           <the status of the job. One of 'WAITING', 'RUNNING', 'DONE', 'STOPPED'>,
                    'results': [
                        {
                            'uuid':         <unique ID of the node>,
                            'timestamp':    <timestamp of the node>,
                            'showProb':     <probability the node in question should be shown>,
                            'hideProb':     <probability the node in question should be hidden>,
                            'recommended':  <SHOW/ HIDE>
                        },
                        ...
                        {
                            'uuid':         <unique ID of the node>,
                            'timestamp':    <timestamp of the node>,
                            'showProb':     <probability the node in question should be shown>,
                            'hideProb':     <probability the node in question should be hidden>,
                            'recommended':  <SHOW/ HIDE>
                        }
                    ]
                }

            (3) action == 'stop'
                {
                    'id':                     <the job id>,
                    'status':                 <the status of the job. in this case 'STOPPED'>
                }
    """

    methods = ['GET']
    valid_actions = ['results', 'status', 'stop']
    valid_args = ['id', 'action']

    def validate_input(self):
        """

        :return:        True - if the input is valid
                        False - otherwise
        """
        if request.method not in self.methods:
            return False, "Invalid method: %s" % request.method

        data = request.args.to_dict()

        if len(data) != len(self.valid_args):
            return False, "Invalid number of arguments: %d. Expected %d" % (len(data), len(self.valid_args))

        for arg in self.valid_args:
            if arg not in data:
                return False, "Required argument: %s" % arg

        for action in self.valid_actions:
            if data['action'] == action:
                return True, "Valid!"

        return False, "Invalid action name: %s" % data['action']

    def dispatch_request(self):

        sts, msg = self.validate_input()

        if not sts:
            return Response(
                status=400,
                response=msg
            )

        # TODO: finish implementation here

        return Response(200)


class CacheResetView(View):
    """
        View class that handles requests that cause the cache database to be cleaned.

        Path: /reset-cache?forced=<True/False>
        Methods: PUT

        The 'forced' flag here is optional. By default, it will be set to False.
        When set to True, it will forcibly delete any running jobs and then clears the cache.
        Otherwise, it will return with HTTP code 400 (Invalid request) if there is a job running.
    """
    methods = ['PUT']

    def validate_input(self):
        """

        :return:        - False, error_message   -   if the input is invalid
                        - True, 'Success'        -   if the input is valid
        """
        if request.method not in self.methods:
            return False, 'Invalid request: %s' % request.method

        data = request.args.to_dict()

        if len(data) == 0:
            return True, 'Success'

        if len(data) != 1:
            return False, 'Too many arguments provided: %d. Expected 1.' % len(data)

        if 'forced' not in data:
            return False, 'Invalid argument: %s' % data.keys()[0]

        if not isinstance(data['forced'], bool):
            return False, 'Invalid argument type. Expected bool, got %s' % str(type(data['forced']))

        return True, 'Success'

    def dispatch_request(self):

        sts, msg = self.validate_input()
        if not sts:
            return Response(
                status=400,
                response=msg
            )

        # TODO: finish implementation

        return Response(200)
