from neo4j.v1 import GraphDatabase, basic_auth

class DatabaseDriver:
    def __init__(self, host, usrname, passwd):
        """
                CONSTRUCTOR

        :param host:        The host where the Neo4J server runs on
        :param usrname:     The username used for authentication
        :param passwd:      The password used for authentication
        """
