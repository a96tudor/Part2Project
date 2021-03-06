"""
Part2Project -- exceptions.py

Copyright Mar 2018 [Tudor Mihai Avram]

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


class CustomException(Exception):
    """
        Class representing a general error in the system
    """

    def __init__(self,
                 msg: str):
        """

        :param msg:         The message we want to display
        """
        self._message = msg
        Exception(self, CustomException).__init__()

    def __str__(self):
        """

        :return:        The message for the exception
        """
        return self._message
