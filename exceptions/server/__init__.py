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
from exceptions import CustomException


class InvalidJobStatus(CustomException):

    def __init__(self,
                 status,
                 valids):

        message = "Invalid job status provided. Expected %s, got %s." % (", ".join(valids), status)

        CustomException.__init__(self, message)