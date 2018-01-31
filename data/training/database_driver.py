from py2neo import Graph, Node
import os


class DatabaseDriver:

    def __init__(self, host, usrname, passwd, port):
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

        self._NODES_OF_INTEREST = [
            'File', 'Process', 'Socket', 'Machine'
        ]

    def execute_query(self, query):
        """

        :param query:       The query we want to execute

        :return:            The query results, as a list
        """
        results = list(self._graph.data(query))

        return results

