"""
Part2Project -- __init__.py.py

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
from data.neo4J.database_driver import AnotherDatabaseDriver
from data.features.feature_extractor import FeatureExtractor
from data.features.constants import SUPPORTED_FILE_FORMATS, FEATURES_ONE_HOT
from cypher_statements.config import RULES_TO_RUN
import pandas as pd

import json
from data.utils import shuffle_dict, dump_json


def get_dataset(driver: AnotherDatabaseDriver,
                nodes: list,
                shuffle: bool = False,
                for_gat: bool = False,
                include_NONE: bool=True):
    """

    :param driver:              The neo4j database driver used in this case
    :param nodes:               The nodes for which we extract the features
    :param shuffle:             Whether to shuffle the nodes after extracting the feature vectors or not.
                                Default False.
    :param for_gat:             Whether we include the neighbours or not (i.e. when doing this for GAT.
                                Default False.
    :param include_NONE:        Whether we include the invalid node entries as None or not.
                                Default True.

    :return:                    A dictionary containing the feature vectors extracted
    """

    feature_extractor = FeatureExtractor(
        nodes=nodes,
        driver=driver
    )

    features = feature_extractor.get_feature_matrix(include_NONE=include_NONE)

    print(features)

    if not for_gat:
        if not shuffle:
            return features
        else:
            features = shuffle_dict(features)
            return features

    neighs = feature_extractor.get_neighbours()

    extracted = feature_extractor

    for node in features:
        if len(neighs[node]) == 0:
            features[node]['neighs'][0] = features[node]['self']
        else:
            to_extract = list()
            features[node]['neighs'] = list()
            for neigh in neighs[node]:
                tp = (neigh['uuid'], neigh['timestamp'], )
                if tp in extracted:
                    if extracted[tp]['self'] is not None:
                        features[node]['neighs'].append(extracted[tp]['self'])
                else:
                    to_extract.append(neigh)

            fe = FeatureExtractor(
                nodes=to_extract,
                driver=driver,
                verbose=True
            )

            new_nodes = fe.get_feature_matrix(include_NONE=False)

            for neigh in new_nodes:
                features[node]['neighs'].append(new_nodes[neigh]['self'])

            extracted = extracted + new_nodes

    if not shuffle:
        return features
    else:
        features = shuffle_dict(features)
        return features


def build_training_set(host: str,
                       port: int,
                       user: str,
                       password: str,
                       for_gat: bool = False,
                       save_to_disk: bool = True,
                       save_in_format: str = 'df',
                       save_in_dir: str = 'data/datasets/',
                       filename: str = None,
                       limit_per_rule: int=1000):
    """

            Method that builds a training set based on a set
            of ground-truths.

    :param host:                    the host name for the Neo4J connection
    :param port:                    the port number for the Neo4J connection
    :param user:                    the username for the Neo4J connection
    :param password:                the password for the Neo4J connection
    :param for_gat:                 If the dataset that is being built is for GAT or not.
                                    In other words, if we include information about the
                                    neighbours of the node or not.
                                    Default False.
    :param save_to_disk:            If we want to save the dataset to disk or not.
                                    Default True.
    :param save_in_format:          The format the file is saved in.
                                    Currently supported formats: 'json', 'df'
                                    Default 'df'
    :param save_in_dir:             Directory where the training set should be saved.
                                    Default: 'data/datasets/'
    :param filename:                Name of the file where the dataset should be saved.
                                    Default None.
    :param limit_per_rule:          Up to how many nodes to return for every rule
                                    Default 1000.

    :return:                        The dataset, as a dictionary. - if successful
                                    None                          - otherwise
    """
    # ASSERTIONS
    assert(save_in_format in SUPPORTED_FILE_FORMATS)
    if for_gat and save_in_format == 'df':
        print("When saving dataset for GAT, the 'df' format is unavailable")
        return None
    if save_to_disk:
        assert(filename is not None)

    # ACTUAL IMPLEMENTATION
    print("======================================")
    print("======= Starting to build the ========")
    print("=========== training set =============")
    print("======================================")

    driver = AnotherDatabaseDriver(
        host=host,
        port=port,
        user=user,
        pswd=password
    )

    print("Connected to the database!")

    query = "match (x)" \
            "where not 'Machine' in labels(x) and not 'Pipe' in labels(x) and not 'Meta' in labels(x) and labels(x) <> ['Global']" \
            "return x.uuid as uuid, x.timestamp as timestamp"

    full_results = dict()

    all_nodes = driver.execute_query(query)
    nodes_cnt = len(all_nodes)

    show_nodes = list()

    print("%d nodes to process. Getting to work!" % nodes_cnt)

    for rule_file in RULES_TO_RUN:
        print("Running rule from %s..." % rule_file)
        with open(rule_file) as f:
            rule_query = f.read()
            result = driver.execute_query(rule_query)

            for node in result:
                try:
                    all_nodes.pop(all_nodes.index(node))
                except ValueError:
                    # It is not in the list, so we don't add it again :D
                    result.pop(result.index(node))

            result = result[:min(len(result), limit_per_rule)]

            features = get_dataset(
                driver=driver,
                nodes=result,
                for_gat=for_gat,
                include_NONE=False,
                shuffle=False
            )

            show_nodes = show_nodes + result

            for node in features:
                features[node]['SHOW'] = 1
                features[node]['HIDE'] = 0

            print("     Added " + str(len(features)) + " new entries!")

            full_results.update(features)

    # Setting the HIDE nodes limit so that the training set
    # roughly follows the 30-70 distribution of SHOW/HIDE nodes
    # present in the actual database
    limit_for_hide = int((.7/.3) * len(RULES_TO_RUN) * limit_per_rule)

    print("Finished adding all SHOW labeled nodes. Added %d in total.\n" % len(full_results))

    hide_nodes = all_nodes[:min(len(all_nodes), limit_for_hide)]

    print("Moving on to HIDE labeled nodes. %d to add." % len(hide_nodes))

    features = get_dataset(
        driver=driver,
        nodes=hide_nodes,
        for_gat=for_gat,
        include_NONE=False,
        shuffle=False
    )

    for node in features:
        features[node]['SHOW'] = 0
        features[node]['HIDE'] = 1

    full_results.update(features)
    full_results = shuffle_dict(full_results)

    if not save_to_disk:
        return full_results

    if save_in_format == 'json':
        file_path = "%s/%s" % (save_in_dir, filename)

        dump_json(full_results, file_path)
    else:
        df = build_df_from_dict(full_results)
        file_path = "%s/%s" % (save_in_dir, filename)

        df.to_csv(file_path, index=True)

    return full_results


def build_df_from_dict(data: dict):
    """

    :param data:        Dictionary we're building the DataFrame from
    :return:            The resulting dataframe
    """
    df = pd.DataFrame(columns=FEATURES_ONE_HOT + ['SHOW', 'HIDE'])

    for node in data:
        new_entry = data[node]['self']
        new_entry['SHOW'] = data[node]['SHOW']
        new_entry['HIDE'] = data[node]['HIDE']

        new_df = pd.DataFrame(new_entry, index=[0])

        df = pd.concat([df, new_df], axis=0, ignore_index=True)

    return df

