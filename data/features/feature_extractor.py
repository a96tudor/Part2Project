"""
Part2Project -- feature_extractor.py

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

from data.neo4J.database_driver import DatabaseDriver
import pandas as pd
from strings import LINE_DELIMITER
from data.features.constants import *


class FeatureExtractor(object):

    def __init__(self,
                 nodes: list,
                 driver: DatabaseDriver,
                 verbose: bool):
        """
            CONSTRUCTOR

        :param nodes:       List of nodes we want to get the features for.
                            Has to be a list of dictionaries, each entry being:
                                {
                                    'uuid': the unique ID of the node,
                                    'timestamp': the timestamp of the node
                                }
        :param driver:      The driver
        :param verbose:     Set to 'True' if we want the extractor to give constant feedback and 'False' otherwise
        """
        # Asserting inputs
        for node in nodes:
            assert(isinstance(node, dict))
            assert(node.keys() == ['uuid', 'timestamp'])

        assert(driver.connection_active())

        self._nodes = nodes
        self._dbDriver = driver
        self._verbose = True

        if self._verbose:
            print(LINE_DELIMITER)
            print("     Feature extractor initiated")
            print("     {:d} nodes to process".format(len(nodes)))
            print(LINE_DELIMITER)

    def _get_node_type(self,
                       uuid,
                       timestamp):
        """
            Private method that returns the type of the node we want to get the features for

        :param uuid:        The unique ID of the node we're looking for
        :param timestamp:   The timestamp of the node we're looking for

        :return:            The node type, as a string  -  if the uuid and timestamp are valid
                            None                        - otherwise
        """
        q = "match (n: {uuid: '%s', timestamp: %d} return labels(n)" % (uuid, timestamp)

        results = self._dbDriver.execute_query(q)

        if len(results) == 0:
            return None

        return results[0]['labels(n)']


    def _get_closest_neighbour(self,
                               uuid,
                               timestamp,
                               type):
        """
            Private method that returns the closest neighbour to the node

        :param uuid:        The unique ID of the node we're interested in
        :param timestamp:   The timestamp of the node we're interested in
        :param type:        The type of the node we're interested in

        :return:            A dictionary with the following format:

                                {
                                    'type':         the type of the neighbour,
                                    'uuid':         the id of the neighbour,
                                    'timestamp':    the timestamp of the neighbour,
                                    'edge':         the edge type
                                }
                                        - If the parameters provided are valid
                            None        - otherwise
        """

        if type in ['File', 'Socket']:
            # I'm looking for the closest process to it

            q = "match (f: %s {uuid: '%s', timestamp: %d})-[rel:PROC_OBJ]->(p:Process) " \
                "return p.uuid as uuid, " \
                        "p.timestamp as timestamp, " \
                        "rel.state as rel_sts " \
                    "order by abs(p.timestamp-f.timestamp) limit 1" % (type, uuid, timestamp)

            results = self._dbDriver.execute_query(q)

            if len(results) == 0:
                return None

            return {
                'type': 'Process',
                'uuid': results[0]['uuid'],
                'timestamp': results[0]['timestamp'],
                'edge': results[0]['rel_sts']
            }
        else:
            # I'm looking for the file the process was excuted from
            

    def get_feature_matrix(self):
        """

        :return:        A pandas dataframe containing all the features
        """

        result = pd.DataFrame(columns=FEATURES_ONE_HOT)

        for node in self._nodes:
            node_features = dict()

            node_type = self._get_node_type(node['uuid'], node['timestamp'])

            if node_type not in ACCEPTED_NODES:
                # We're not going to care about this entry
                continue

            for feature in NODE_TYPE_FEATURES:
                if NODE_TYPE_FEATURES[feature] == node_type:
                    node_features[feature] = 1.0
                else:
                    node_features[feature] = 0.0



