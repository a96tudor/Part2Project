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
from exceptions.server.cache import *


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

        try:
            self.conn = driver.connect(
                host=host,
                database=dbName,
                user=user,
                password=password,
                port=port
            )
        except driver.OperationalError or driver.DatabaseError:
            raise PostgresDriverConnectionException(
                url="%s:%d" % (host, port),
                dbName=dbName
            )

        self.host = host
        self.port = port
        self.dbName = dbName
        self.user = user
        self.password = password

    def close(self):
        """
            Method that closes the database connection

        :return:    -
        """
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def _execute_query(self,
                       query,
                       *args):
        """

        :param query:                           The query we want to execute
        :param args:                            The arguments to replace the wildcards in the query
        :return:                                -
        :except psycopg2.DatabaseError:         If executing the query fails
        """
        with self.conn.cursor() as cur:
            print(cur)
            cur.execute(query, *args)
            cur.close()
            self.conn.commit()

    def _get_new_connection(self,
                            newHost: str,
                            newPort: str,
                            newDbName: str,
                            newUser: str,
                            newPass: str):
        """

        :param newURL:          The new URL
        :param newDbName:       The new db name
        :param newUser:         The new username
        :param newPass:         The new password
        :return:                The new connection - if successful
                                None               - otherwise
        """

        try:
            newConn = driver.connect(
                host=newHost,
                dbName=newDbName,
                user=newUser,
                password=newPass,
                port=newPort
            )

            return newConn
        except:
            # If an exception is thrown while
            # configuring the new connection,
            # it is unsuccessful. Thus return None
            return None

    def setup_database(self):
        """

        :return:
        """
        for table in DATABASE_SETUP:

            self._execute_query(DATABASE_SETUP[table])
            print("Created the %s table" % table)


    def execute_SELECT(self,
                       query,
                       *args):
        """
                Method that handles the execution of SELECT queries

        :param query:       The query to be executed
        :param args:        The arguments to replace the wildcards in the query
        :return:            The query results, as a list of tuples
        """

        results = None

        with self.conn.cursor() as cur:
            cur.execute_query(query, *args)
            results = cur.fetchall()
            cur.close()

        return results

    def execute_INSERT(self,
                       query,
                       *args):
        """
                Method that handles the execution of INSERT queries

        :param query:      The INSERT to be executed
        :param args:       The arguments for the wildcards in the query
        :return:           -
        """
        with self.conn.cursor() as cur:
            cur.execute(query, *args)
            self.conn.commit()
            cur.close()

    def execute_UPDATE(self,
                       query,
                       *args):
        """

        :param query:
        :param args:
        :return:
        """
        with self.conn.cursor() as cur:
            cur.execute_query(query, *args)
            self.conn.commit()
            cur.close()

    def renew_connection(self,
                         newHost: str,
                         newPort: int,
                         newDbName: str,
                         newUser: str,
                         newPass: str):
        """
            Method that changes the database.
            Returns a boolean status (i.e. successful or not)
            If not successful, the connection does not change.

        :param newHost:         The host of the new database
        :param newPort:         The port of the new database
        :param newDbName:       The name of the new database
        :param newUser:         The username used to connect to the new database
        :param newPass:         The password used to connect to the new database

        :return:                True - if successful
                                False - otherwise
        """
        url = "%s:%d" % (newHost, newPort)

        newConn = self._get_new_connection(url, newDbName, newUser, newPass)

        if newConn is None:
            return False

        self.url = url
        self.dbName = newDbName
        self.user = newUser
        self.password = newPass

        self.conn = newConn

        return True

    def reset_connection(self):
        """
            Method that attempts to reset the
            current connection. Only changes
            the actual inner object if
            the new connection is successful

        :return:        True - if successful
                        False - otherwise
        """
        newConn = self._get_new_connection(
            newURL=self.url,
            newDbName=self.dbName,
            newUser=self.user,
            newPass=self.password
        )

        if newConn is None:
            return False
        else:
            self.conn = newConn
            return True

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
