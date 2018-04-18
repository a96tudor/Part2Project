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

class ClassifyView(View):
    """
        Class representing the general entry point for the API.

        Is expecting a POST request containing a JSON with the following format:
                [
                    ''
                ]
    """
    methods = ['POST']

    expected_values = ['uuid', 'timestamp']

    def validate_input(self):
        """

        :return:        - True if the incoming request is valid
                        - False otherwise
        """
        if request.method not in self.methods:
            return False

        if not request.is_json:
            return False

        data = request.json

        if not isinstance(data, list):
           return False

        for entry in data:
            if not isinstance(entry, dict):
                return False
            for e in self.expected_values:
                if e not in entry:
                    return False

        return True

    def generate_job(self):
        jobsHandler.add_job()

    def dispatch_request(self):
        if not self.validate_input():
            return Response(status=400,
                            response='Invalid input format')

        return Response(200)

