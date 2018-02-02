from data.training import constants as cnst
from data.training.database_driver import DatabaseDriver
from data.training.rules_handler import RulesHandler
import pandas as pd, numpy as np


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

    print("Successfully connected to the database!")

    query = "match (x)" \
            "where not 'Machine' in labels(x) and not 'Meta' in labels(x) " \
            "return count(x) as total"

    _TOTAL_NO_OF_NODES = db.execute_query(query)[0]['total']

    print('There are ' + str(_TOTAL_NO_OF_NODES) + ' nodes to process!')

    rh = RulesHandler(db_driver=db)

    _CURRENT_RULES = {
        'rule1': rh.get_entries_rule_1,
        'rule2': rh.get_entries_rule_2,
        'rule3': rh.get_entries_rule_3,
        'rule4': rh.get_entries_rule_4,
        'rule5': rh.get_entries_rule_5,
        'rule8': rh.get_entries_rule_8,
        'rule9': rh.get_entries_rule_9,
        'rule10': rh.get_entries_rule_10,
        'rule14': rh.get_entries_rule_14
    }

    for rule in _CURRENT_RULES:
        print("Adding nodes defined by "+rule+"... ")
        with open(rules_path + rule + '.cyp') as f:
            rule_query = f.read()
            new_entries = _CURRENT_RULES[rule](db.execute_query(rule_query))

            ts = pd.concat([ts, new_entries])
            print("Added " + str(new_entries.shape[0]) + " new entries!")

    print("=======================================================================")
    print("Finished adding nodes based on rules! Added " + str(ts.shape[0]) + " 1-labeled entries in total!")
    print("Now onto 0-labeled nodes...")
    print('There are ' + str(_TOTAL_NO_OF_NODES - rh.get_1_labeled_count) + ' remaining nodes to process... Getting to work... ')
    print("=======================================================================")

    print("This might take a while...")
    zero_labeled_entries = rh.get_0_labels()

    print("There are " + str(zero_labeled_entries.shape[0]) + ' 0-labeled entries!')

    ts = pd.concat([ts, zero_labeled_entries])

    print("Phiew, finally done!")

    print("=======================================================================")
    print("TOTAL ENTRIES: " + str(ts.shape[0]))
    print("Writing training set to " + training_set_path)
    print("=======================================================================")

    try:
        ts.to_csv(index=False, path_or_buf=training_set_path)
    except:
        print("ERROR writing dataframe to given training set path")
        return False

    print("DONE - Successful!")

    return True

def split_training_set(training_set_path='data/training/training-set.csv',
                       results_path='data/tmp/', training_percentile= .75):
    """

    :param training_set_path:                Path to the CSV file containing the full dataset
    :param results_path:
    :param training_percentile:
    :return:
    """