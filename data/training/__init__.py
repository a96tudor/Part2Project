from data.training import constants as cnst
from data.training.database_driver import DatabaseDriver
from data.training.rules_handler import RulesHandler
import pandas as pd, numpy as np
import os



def generate_training_set(host, port, db_usrname, db_passwd, rules_path, training_set_path):
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

    db = DatabaseDriver(host=host,
                        port=port,
                        usrname=db_usrname,
                        passwd=db_passwd)

    rh = RulesHandler(db_driver=db)

    _CURRENT_RULES = {
        #'rule1': rh.get_entries_rule_1,
        'rule2': rh.get_entries_rule_2
    }

    rule_files = os.listdir(rules_path)

    for rule in _CURRENT_RULES:
        with open(rules_path + rule + '.cyp') as f:
            rule_query = f.read()
            new_entries = _CURRENT_RULES[rule](db.execute_query(rule_query))

            ts = pd.concat([ts, new_entries])

    print(ts)

    print("DONE - Successful!")

    return True