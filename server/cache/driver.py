"""
Part2Project -- driver.py

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
import psycopg2 as driver
from server.cache.constants import *


class PostgresDriver(object):
    """
        Class representing the
    """
    def __init__(self,
                 host,
                 port,
                 dbName,
                 user,
                 password):
        """

        :param host:
        :param port:
        :param dbName:
        :param user:
        :param password:
        """
        url = "%s:%d" % (host, port)

        self.conn = driver.connect(
            host=url,
            dbName=dbName,
            user=user,
            password=password
        )

    def close(self):
        """
            Method that closes the database connection

        :return:    -
        """
        if self.conn is not None:
            self.conn.close()

    def _execute_query(self,
                       query,
                       *args):
        """

        :param query:       The query we want to execute
        :param args:        The arguments to replace the wildcards in the query

        :return:            -
        """
        with self.conn.cursor() as cur:
            cur.execute_query(query, *args)
            cur.close()
            self.conn.commit()

    def setup_database(self):
        """

        :return:
        """
        for table in DATABASE_SETUP:
            try:
                self._execute_query(DATABASE_SETUP[table])
                print("Created the %s table" % table)

            except(Exception, driver.DatabaseError) as erorr:
                print("Error while creating table %s" % table)

    def __exit__(self,
                 exc_type,
                 exc_val,
                 exc_tb):
        """
            Method executed when the process is exited

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close()
