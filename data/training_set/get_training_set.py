
import argparse


def init_database_driver():
    """
        Method that parses the input arguments to the script and returns
            the resulting Neo4J driver, based on the given credentials
    :return:
    """
    database = GraphDatabase.driver(
        'bolt://localhost',
        auth=basic_auth('neo4j', passwd)
    )

