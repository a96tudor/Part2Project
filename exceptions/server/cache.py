"""
Part2Project -- cache.py

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


class PostgresDriverConnectionException(CustomException):
    """
        Class representing a connection exception to the cache database
    """
    def __init__(self,
                 url: str,
                 dbName: str):

        message = "Connection to database %s at %s failed!" % (url, dbName)
        CustomException.__init__(self, message)


class PostgresDriverQueryException(CustomException):
    """
        Class representing a query exception of from the database driver
    """
    def __init__(self,
                 query: str):

        message = "Failed to execute the following query: %s" % query
        CustomException.__init__(self, message)


class PostgressNoActiveConnection(CustomException):

    def __init__(self):
        message = "No active database connection!"
        CustomException.__init__(self, message)


