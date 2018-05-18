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
from flask import request, Response, jsonify
from server import utils
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

        If successful, returns a JSON with the following format:
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
        jobID = utils.jobsHandler.add_job(nodes)

        return jobID

    def dispatch_request(self):
        sts, msg = self.validate_input()

        if not sts:
            return Response(
                status=400,
                response=msg
            )

        if not isinstance(utils.jobsHandler, JobsHandler):
            return Response(
                status=500,
                response='Internal error'
            )

        response = dict()

        try:
            id = utils.jobsHandler.add_job(request.json['nodes'])

            if id is None:
                return Response(
                    status=500,
                    response='Maximum number of running jobs achieved'
                )

            response['status'] = 'Success'
            response['jobID'] = id
            response['caching_active'] = True
            response['nodes_to_process'] = len(request.json['nodes'])

            return jsonify(response)

        except Exception:
            return Response(
                status=500,
                response='Internal error'
            )


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

        args = request.args.to_dict()
        id = args['id']
        action = args['action']

        if action == 'status':
            status = utils.cacheHandler.get_job_status(id)
            if status is None:
                return Response(
                    status=400,
                    response='Invalid job id'
                )

            data = {
                'id': id,
                'status': status
            }

            return jsonify(data)

        else:
            data = utils.cacheHandler.get_nodes_for_job(id)

            if data is None:
                return Response(
                    status=400,
                    response='Invalid job id'
                )

            return jsonify(data)


class CacheResetView(View):
    """
        View class that handles requests that cause the cache database to be cleaned.

        Path: /reset-cache
        Methods: GET

    """
    methods = ['GET']

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

        utils.cacheHandler.clear_cache()

        return Response(200)
