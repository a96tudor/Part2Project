from data.features import constants as cnst
from data.neo4J.database_driver import DatabaseDriver, AnotherDatabaseDriver
from data.training.rules_handler import RulesHandler
import pandas as pd, numpy as np
from data.features.feature_extractor import FeatureExtractor


def generate_training_set(host,
                          port,
                          db_usrname,
                          db_passwd,
                          rules_path,
                          training_set_path):
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

    LIMIT = 1000

    show_nodes = list()

    print("Started building the training set ...")

    ts = pd.DataFrame(columns=(cnst.FEATURES_ONE_HOT + ['SHOW', 'HIDE']))

    db = AnotherDatabaseDriver(
            host=host,
            port=port,
            user=db_usrname,
            pswd=db_passwd
    )

    print("Successfully connected to the database!")

    query = "match (x)" \
            "where not 'Machine' in labels(x) and not 'Pipe' in labels(x) and not 'Meta' in labels(x) and labels(x) <> ['Global']" \
            "return x.uuid as uuid, x.timestamp as timestamp"

    all_nodes = db.execute_query(query)
    _TOTAL_NO_OF_NODES = len(all_nodes)

    print('There are ' + str(_TOTAL_NO_OF_NODES) + ' nodes to process!')

    CURRENT_RULES = [
        'rule1',
        'rule2',
        'rule3',
        'rule4',
        'rule5',
        'rule8',
        'rule9',
        'rule10',
        'rule14'
    ]

    for rule in CURRENT_RULES:
        print("Adding nodes defined by "+rule+"... ")
        with open(rules_path + rule + '.cyp') as f:
            rule_query = f.read()
            result = db.execute_query(rule_query)
            show_nodes = show_nodes + result

            for node in result:
                try:
                    all_nodes.pop(all_nodes.index(node))
                except ValueError:
                    # It is not in the list, so we don't add it again :D
                    result.pop(result.index(node))

            extractor = FeatureExtractor(result[:min(LIMIT, len(result))], db, verbose=True)

            new_entries = extractor.get_feature_matrix()
            new_entries['HIDE'] = pd.Series(np.zeros(len(new_entries)))
            new_entries['SHOW'] = pd.Series(np.ones(len(new_entries)))

            ts = pd.concat([ts, new_entries], ignore_index=True)
            print("     Added " + str(new_entries.shape[0]) + " new entries!")

    LIMIT_HIDE_NODES = 20000
    hide_nodes = all_nodes[:min(LIMIT_HIDE_NODES, len(all_nodes))]

    print("=======================================================================")
    print("Finished adding nodes based on rules! Added " + str(ts.shape[0]) + " 1-labeled entries in total!")
    print("Now onto 0-labeled nodes...")
    print('There are ' + str(_TOTAL_NO_OF_NODES - len(show_nodes)) + ' remaining nodes to process... Getting to work... ')
    print("=======================================================================")

    print("This might take a while...")
    extractor = FeatureExtractor(
        hide_nodes, db, verbose=True
    )

    new_entries = extractor.get_feature_matrix()
    new_entries['HIDE'] = pd.Series(np.ones(len(new_entries)))
    new_entries['SHOW'] = pd.Series(np.zeros(len(new_entries)))

    ts = pd.concat([ts, new_entries], ignore_index=True)

    print("Phiew, finally done!")

    print("=======================================================================")
    print("TOTAL ENTRIES: " + str(ts.shape[0]))
    print("Writing training set to " + training_set_path)
    print("=======================================================================")

    try:
        ts.to_csv(index=True, path_or_buf=training_set_path)
    except:
        print("ERROR writing dataframe to given training set path")
        return False

    print("DONE - Successful!")

    return True
