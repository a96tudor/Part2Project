"""
Part2Project -- database_driver.py

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
from py2neo import Graph, Node
from neo4j.v1 import GraphDatabase


class DatabaseDriver(object):
    """
        Class connecting to the Neo4J database
    """
    def __init__(self,
                 host: str,
                 usrname: str,
                 passwd: str,
                 port: int):
        """
                CONSTRUCTOR

        :param host:        The IP address of the host where the Neo4J server runs on
        :param port:        The port we're connecting to
        :param usrname:     The username used for authentication
                                - None if no authentication required
        :param passwd:      The password used for authentication
                                - None if no authentication required
        """
        self._graph = Graph(
            usrname=usrname,
            password=passwd,
            host=host,
            http_port=port
        )
        self._host = host
        self._port = port

    def execute_query(self,
                      query: str):
        """

        :param query:       The query we want to execute

        :return:            The query results, as a list
        """
        results = list(self._graph.data(query))

        return results

    def connection_active(self):
        """
            Method that checks if the connection to the database is still active or not

        :return:            True - if the connection is active
                            False - otherwise
        """
        if self._graph is None:
            return False

        try:
            a = list(self._graph.data('match (n) return n limit 1'))
            if len(a) == 1:
                return True
            else:
                return False
        except:
            return False

    def __str__(self):

        return "Neo4J connection to host {:s} on port {:d}".format(self._host, self._port)


class AnotherDatabaseDriver(object):
    """
        Class connecting to the Neo4J database
    """

    def __init__(self,
                 host: str,
                 port: int,
                 user: str,
                 pswd: str):
        """
                CONSTRUCTOR

        :param host:            IP address/ DNS name of the host where the Neo4J
                                database is running
        :param port:            The TCP port where the Neo4J database is running
        :param user:            Username used to login to the database
        :param pswd:            Password used to loing to the database
        """

        uri = "%s:%d" % (host, port)

        self._driver = GraphDatabase.driver(uri, auth=(user, pswd), encrypted=False)

    def execute_query(self,
                      query: str,
                      **kwargs):
        """
                Method that executes a given query and returns its result,
                as a list of dictionaries.

        :param query:           The query to be executed
        :param kwargs:          The other parameters that are required for the query
        :return:
        """
        session = self._driver.session()

        result = session.read_transaction(
            lambda tx: tx.run(query)
        )

        records = result.records()
        result = list()

        for r in records:
            result.append(dict(r.items()))

        session.close()

        return result

    def close(self):
        """
            Method that closes the database connection

        :return:        -
        """

        self._driver.close()

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.close()