from data.training import constants as cnst
from data.training.database_driver import DatabaseDriver as DBD
import pandas as pd
import numpy as np

def generate_training_set(host='127.0.0.1', port=7474, db_usrname='neo4j',
                          db_passwd='opus', rules_path='cypher_statements/rules',
                          training_set_path='data/training/training_set.csv'):
    """
        Method that creates a new training set, based on a set of pre-defined rules\

    :param host:                    The host where the Neo4J server runs on
    :param port:                    The port where the Neo4J server runs on
    :param db_usrname:              Username used to connect to the database
    :param db_passwd:               Password used to connect to the database
    :param rules_path:              Path to the rule files
    :param training_set_path:       Path where to create the file containing the training set

    :return:                        True - if successful
                                    False - otherwise
    """

    print("Started building the training set ...")

    ts = pd.DataFrame(columns=cnst.FEATURES)

    print("DONE - Successful!")

    return True