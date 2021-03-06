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

from data.neo4J.database_driver import AnotherDatabaseDriver
import pandas as pd
from strings import LINE_DELIMITER, PROGRESS_REPORT
from data.features.constants import *
import numpy as np


class FeatureExtractor(object):
    """
        Class representing a Feature Extractor. Main entry point
        for the Neo4J interaction module
    """

    def __init__(self,
                 nodes: list,
                 driver: AnotherDatabaseDriver,
                 verbose: bool = False):
        """
            CONSTRUCTOR

        :param nodes:       List of nodes we want to get the features for.
                            Has to be a list of dictionaries, each entry being:
                                {
                                    'uuid': the unique ID of the node,
                                    'timestamp': the timestamp of the node
                                }
        :param driver:      The driver
        :param verbose:     Set to 'True' if we want the extractor to give constant feedback and 'False' otherwise.
                            Default True
        """
        # Asserting inputs
        for node in nodes:
            assert(isinstance(node, dict))
            assert(list(node.keys()) == ['uuid', 'timestamp'])

        self._nodes = nodes
        self._dbDriver = driver
        self._verbose = verbose

        if self._verbose:
            print(LINE_DELIMITER)
            print("     Feature extractor initiated")
            print("     {:d} nodes to process".format(len(nodes)))
            print(LINE_DELIMITER)

    def _get_node_type(self,
                       uuid: str,
                       timestamp: int):
        """
            Private method that returns the type of the node we want to get the features for

        :param uuid:        The unique ID of the node we're looking for
        :param timestamp:   The timestamp of the node we're looking for

        :return:            The node type, as a string  -  if the uuid and timestamp are valid
                            None                        - otherwise
        """
        q = "match (n {uuid: '%s', timestamp: %d}) return labels(n)" % (uuid, timestamp)

        results = self._dbDriver.execute_query(q)

        if len(results) == 0:
            return None

        labels = results[0]['labels(n)']

        for l in labels:
            if l in ACCEPTED_NODES:
                return l
        return None

    def _get_closest_neighbour(self,
                               uuid: str,
                               timestamp: int,
                               type: str):
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
                                    'edge':         the edge type,
                                    'dist':         distance in epochs from the neighbour
                                }
                                        - If the parameters provided are valid
                            None        - otherwise
        """

        if type in ['File', 'Socket']:
            # I'm looking for the closest Process to it

            q = "match (f: %s {uuid: '%s', timestamp: %d})-[rel:PROC_OBJ]->(p:Process) " \
                "return p.uuid as uuid, " \
                        "p.timestamp as timestamp, " \
                        "rel.state as rel_sts " \
                    "order by abs(p.timestamp-f.timestamp) limit 1" % (type, uuid, timestamp)

            results = self._dbDriver.execute_query(q)

            if len(results) == 0:
                #print("This the reason - File/ Socket")
                #print(q)
                return None

            return {
                'type': 'Process',
                'uuid': results[0]['uuid'],
                'timestamp': results[0]['timestamp'],
                'edge': results[0]['rel_sts'],
                'dist': abs(timestamp - results[0]['timestamp'])
            }
        else:
            # I'm looking for the File the Process was excuted from
            # or for the closest Socket to the Process. The actual
            # result is going to be the one that is closest to the Process (time-wise)

            q_file = "match (f: File)-[rel:PROC_OBJ]->(p:Process {uuid: '%s', timestamp: %d}) " \
                        "return f.uuid as uuid, " \
                        "f.timestamp as timestamp, " \
                        "rel.state as rel_sts " \
                    "order by abs(p.timestamp-f.timestamp) limit 1" % (uuid, timestamp)

            q_socket = "match (s: Socket)-[rel:PROC_OBJ]->(p:Process {uuid: '%s', timestamp: %d}) " \
                            "return s.uuid as uuid, " \
                            "s.timestamp as timestamp, " \
                            "rel.state as rel_sts " \
                        "order by abs(p.timestamp-s.timestamp) limit 1" % (uuid, timestamp)

            closest_file = self._dbDriver.execute_query(q_file)
            closest_socket = self._dbDriver.execute_query(q_socket)

            if len(closest_file) == 0 and len(closest_socket) == 0:
                #print("This is the reason - Process")
                #print(q_socket)
                #print(q_file)
                return None

            if len(closest_file) == 0:
                return {
                    'type': 'Socket',
                    'uuid': closest_socket[0]['uuid'],
                    'timestamp': closest_socket[0]['timestamp'],
                    'edge': closest_socket[0]['rel_sts'],
                    'dist': abs(timestamp - closest_socket[0]['timestamp'])
                }

            if len(closest_socket) == 0:
                return {
                    'type': 'File',
                    'uuid': closest_file[0]['uuid'],
                    'timestamp': closest_file[0]['timestamp'],
                    'edge': closest_file[0]['rel_sts'],
                    'dist': abs(timestamp - closest_file[0]['timestamp'])
                }

            argmin = 'File' \
                if abs(closest_socket[0]['timestamp'] - timestamp) > abs(closest_file[0]['timestamp'] - timestamp) \
                    else 'Socket'

            return {
                'type': argmin,
                'uuid': closest_file[0]['uuid'] if argmin == 'File' else closest_socket[0]['uuid'],
                'timestamp': closest_file[0]['timestamp'] if argmin == 'File' else closest_socket[0]['timestamp'],
                'edge': closest_file[0]['rel_sts'] if argmin == 'File' else closest_socket[0]['rel_sts'],
                'dist': min(abs(timestamp - closest_file[0]['timestamp']), abs(timestamp - closest_socket[0]['timestamp']))
            }

    def _process_is_connected(self,
                              uuid: str,
                              timestamp: int):
        """

            Private method that checks whether a given Process is connected to the web or not

        :param uuid:            unique ID of the Process
        :param timestamp:       timestamp of the Process

        :return:                1.0 - if the Process is connected
                                0.0 - otherwise
        """
        query = 'match (p:Process {uuid: "%s", timestamp: %d})-[:PROC_OBJ]->(s:Socket)' \
                    ' where not s.name[0]=~"127.0.0.1.*" ' \
                'return 1' % (uuid, timestamp)

        results = self._dbDriver.execute_query(query)

        return 1.0 if len(results) > 0 else 0.0

    def _file_is_downloaded(self,
                            uuid: str,
                            timestamp: int):
        """

            Private method that checks if a File was downloaded from the web
            (also checks for previous versions of the file)

        :param uuid:            the unique ID of the File
        :param timestamp:       the timestamp of the

        :return:                1.0 - if the File was downloaded
                                0.0 - otherwise
        """
        query = 'match (f:File {uuid: "%s"})-[fp:PROC_OBJ]->(p:Process)<-[sp:PROC_OBJ]-(s:Socket)' \
                    'where f.timestamp <= %d and ' \
                           '(fp.state="WRITE" or fp.state="RaW" or fp.state="NONE") and ' \
                           '(sp.state="CLIENT" or fp.state="RaW") and ' \
                           'not s.name[0]=~"127.0.0.1.*"' \
                'return f.uuid' % (uuid, timestamp)

        results = self._dbDriver.execute_query(query)

        return 1.0 if len(results) != 0 else 0.0

    def _socket_is_connected(self,
                             uuid: str,
                             timestamp: int):
        """
            Private method that checks if a Socket is connected to an external machine or not

        :param uuid:            The unique ID of the Socket in question
        :param timestamp:       The timestamp of the Socket in question

        :return:                1.0 if it connects to an external machine
                                0.0 otherwise
        """
        q = 'match (s:Socket {uuid: "%s", timestamp: %d}) ' \
                'where not s.name[0]=~"127.0.0.1.*"' \
            'return 1' % (uuid, timestamp)

        results = self._dbDriver.execute_query(q)

        return 1.0 if len(results) != 0 else 0.0

    def _process_uid_gid_sts(self,
                             uuid: str,
                             timestamp: int):
        """
                Private method that checks if, for a given process, uid == euid and gid == egid

        :param uuid:            Unique ID of the process in question
        :param timestamp:       Timestamp used to identify the process version

        :return:                UID_STS:   1 if uid == euid
                                           0 otherwise

                                GID_STS:   1 if gid == egid
                                           0 otherwise
        """
        query = 'match (p:Process {uuid: "' + uuid +'", timestamp: ' + str(timestamp) + '})' \
                'return p.meta_uid = p.meta_euid as uid_sts, ' \
                       'p.meta_gid = p.meta_egid as gid_sts'

        results = self._dbDriver.execute_query(query)

        return 1.0 if results[0]['uid_sts'] else 0.0, \
               1.0 if results[0]['gid_sts'] else 0.0

    def _get_version_number(self,
                            uuid: str,
                            timestmap: int):
        """

        :param uuid:        The unique ID of the node we want to find the version number for
        :param timestamp:   The timestamp of the current node version

        :return:            The version number, as a float
        """
        query = 'match (x {uuid: "%s"})' \
                    'where x.timestamp < %d ' \
                'return x.timestamp order by x.timestamp' % (uuid, timestmap)

        previous_timestamps = self._dbDriver.execute_query(query)

        return float(len(previous_timestamps))

    def _is_suspicious(self,
                       uuid: str,
                       timestamp: int,
                       type: str):
        """

        :param uuid:            unique ID of the node
        :param timestamp:       timestamp of the node
        :param type:            type of node we want to check

        :return:                1.0  -  if the node can be considered suspicious
                                0.0  -  otherwise
        """
        q = "match (n {uuid: '%s', timestamp: %d}) " \
            "return n.name as name, n.cmdline as cmd" % (uuid, timestamp)

        result = self._dbDriver.execute_query(q)

        if type == 'File':
            name = result[0]['name']

            if name is None:
                return 1.0
            else:
                name = name[0]

            if any(sub_str in name for sub_str in BLACKLIST['File']):
                return 1.0
            else:
                return 0.0

        else:
            # It is a process
            cmd = result[0]['cmd']

            if cmd is None:
                return 1.0

            if any(sub_str in cmd for sub_str in BLACKLIST['Process']):
                return 1.0

            # Otherwise, we need to check if it writes to any file in a location that is not safe,
            # or if the file acting as its binary is on the blacklist
            query = 'match (p:Process {uuid: "%s", timestamp: %d})<-[rel:PROC_OBJ]-(f:File) ' \
                    'return rel.state, f.name, f.uuid, f.timestamp' % (uuid, timestamp)

            q_results = self._dbDriver.execute_query(query)

            for result in q_results:
                if result['rel.state'] == 'BIN' and self._is_suspicious(
                        result['f.uuid'], result['f.timestamp'], 'File') == 1.0:
                    return 1.0
                if result['rel.state'] != 'READ':
                    if any(sub_str in result['f.name'] for sub_str in DANGEROUS_LOCATIONS):
                        return 1.0

            # If nothing bad so far, all good. return 0

            return 0.0

    def _file_is_external(self,
                          uuid: str,
                          timestamp: int):
        """
                Private method that checks if a file is external (i.e. whether its
            contents are transmitted via a Socket to a different machine)

        :param uuid:            The unique ID of the file in question
        :param timestamp:       Used to identify the given version of the file

        :return:                1 - if external
                                0 - otherwise
        """
        query = 'match (f:File {uuid: "%s", timestamp: %d})-' \
                        '[rel_fp:PROC_OBJ]->(p:Process)<-[rel_sp:PROC_OBJ]-(s:Socket) ' \
                    'where rel_fp.state <> "BIN" ' \
                'return f.uuid' % (uuid, timestamp)

        results = self._dbDriver.execute_query(query)

        return 1.0 if len(results) != 0 else 0.0

    def _get_neighbours_for_node(self,
                                 uuid: str,
                                 timestamp: int):
        """

        :param uuid:            The unique ID of the node in question
        :param timestamp:       The timestamp of the node in question

        :return:                A list of all the neighbours of the node,
                                represented as (uuid, timestamp) pairs
        """
        query = 'match (n {uuid: "%s", timestamp: %d}) -- (m)' \
                    'where ("File" in labels(m) or "Process" in labels(m) or "Socket" in labels(m))' \
                        'and (m.uuid <> "%s" or m.timestamp <> %d)' \
                'return m.uuid as uuid, m.timestamp as timestamp' % (uuid, timestamp, uuid, timestamp)

        neighs = self._dbDriver.execute_query(query)

        return neighs

    def _get_node_degree(self,
                         uuid: str,
                         timestamp: int):
        """
                Private method that gets the degree of a specific node

        :param uuid:            The unique ID of the node we're interested in
        :param timestamp:       The timestamp of the node we're interested in

        :return:                The resulting degree
        """

        q = "match (n) " \
                "with n, size((n)--()) as degree " \
            "where n.uuid = '%s' and n.timestamp = %d " \
            "return degree" % (uuid, timestamp)

        result = self._dbDriver.execute_query(q)

        if len(result) == 0:
            return None

        return result[0]['degree']

    def get_feature_matrix(self,
                           include_NONE=True):
        """

        :param include_NONE:    Whether we want to include the nodes we failed to get a
                                feature vector for as 'NONE' or not. Default True
        :return:                A pandas dict containing all the features
        """

        result = list()
        cnt_done = 0

        if self._verbose:
            # Setting up log data
            cnt_done = 0
            total = len(self._nodes)
            last_step = 0
            print("Building feature matrix...")
            print(PROGRESS_REPORT[last_step] % (cnt_done, total))

        for node in self._nodes:
            node_features = dict()

            """
                NODE TYPES
            """
            if any(node[x] is None for x in node):
                if include_NONE:
                    result.append({
                        'id': (node['uuid'], node['timestamp'], ),
                        'self': None
                    })
                continue

            node_type = self._get_node_type(node['uuid'], node['timestamp'])

            if node_type not in ACCEPTED_NODES:
                # We're not going to care about this entry
                if include_NONE:
                    result.append({
                        'id': (node['uuid'], node['timestamp'], ),
                        'self': None
                    })
                continue

            for feature in NODE_TYPE_FEATURES:
                if NODE_TYPE_FEATURES[feature] == node_type:
                    node_features[feature] = 1.0
                else:
                    node_features[feature] = 0.0

            deg = self._get_node_degree(node['uuid'], node['timestamp'])

            if deg is None:
                if include_NONE:
                    result.append({
                        'id': (node['uuid'], node['timestamp'], ),
                        'self': None
                    })
                    continue
            node_features['DEGREE'] = deg

            """
                NEIGH_TYPE and EDGE_TYPE and NEIGH_DIST and NEIGH_DEGREE
            """
            neigh_data = self._get_closest_neighbour(
                node['uuid'],
                node['timestamp'],
                node_type
            )

            if neigh_data is None:
                if include_NONE:
                    result.append({
                        'id': (node['uuid'], node['timestamp'], ),
                        'self': None
                    })
                continue

            if any(neigh_data[x] is None for x in neigh_data):
                if include_NONE:
                    result.append({
                        'id': (node['uuid'], node['timestamp'], ),
                        'self': None
                    })
                continue

            if neigh_data['type'] not in ACCEPTED_NODES:
                # We're not going to care about this entry
                if include_NONE:
                    result.append({
                        'id': (node['uuid'], node['timestamp'], ),
                        'self': None
                    })
                continue

            for feature in NEIGH_TYPE_FEATURES:
                if NEIGH_TYPE_FEATURES[feature] == neigh_data['type']:
                    node_features[feature] = 1.0
                else:
                    node_features[feature] = 0.0

            for feature in EDGE_TYPE_FEATURES:
                if EDGE_TYPE_FEATURES[feature] == neigh_data['edge']:
                    node_features[feature] = 1.0
                else:
                    node_features[feature] = 0.0

            node_features['NEIGH_DIST'] = np.log(neigh_data['dist']) if neigh_data['dist'] != 0 else 0.0
            node_features['NEIGH_DEGREE'] = self._get_node_degree(neigh_data['uuid'], neigh_data['timestamp'])

            """
                WEB_CONN and NEIGH_WEB_CONN
            """

            if node_type == 'Socket':
                node_features['WEB_CONN'] = self._socket_is_connected(
                    node['uuid'], node['timestamp']
                )
                node_features['NEIGH_WEB_CONN'] = self._process_is_connected(
                    neigh_data['uuid'], neigh_data['timestamp']
                )
            elif node_type == 'File':
                node_features['WEB_CONN'] = self._file_is_downloaded(
                    node['uuid'], node['timestamp']
                )
                node_features['NEIGH_WEB_CONN'] = self._process_is_connected(
                    neigh_data['uuid'], neigh_data['timestamp']
                )
            else:
                node_features['WEB_CONN'] = self._process_is_connected(
                    node['uuid'], node['timestamp']
                )
                if neigh_data['type'] == 'File':
                    node_features['NEIGH_WEB_CONN'] = self._file_is_downloaded(
                        neigh_data['uuid'], neigh_data['timestamp']
                    )
                else:
                    node_features['NEIGH_WEB_CONN'] = self._socket_is_connected(
                        neigh_data['uuid'], neigh_data['timestamp']
                    )

            """
                UID & GID sts
            """

            if node_type == 'Process':
                node_features['UID_STS'], node_features['GID_STS'] = self._process_uid_gid_sts(
                    node['uuid'], node['timestamp']
                )
            else:
                node_features['UID_STS'], node_features['GID_STS'] = self._process_uid_gid_sts(
                    neigh_data['uuid'], neigh_data['timestamp']
                )

            """
                VERSION
            """

            node_features['VERSION'] = self._get_version_number(
                node['uuid'], node['timestamp']
            )

            """
                SUSPICIOUS
            """
            if node_type == 'Socket':
                node_features['SUSPICIOUS'] = self._is_suspicious(
                    neigh_data['uuid'], neigh_data['timestamp'], 'Process'
                )
            else:
                node_features['SUSPICIOUS'] = self._is_suspicious(
                    node['uuid'], node['timestamp'], node_type
                )

            """
                EXTERNAL
            """
            if node_type in ['Socket', 'Process']:
                node_features['EXTERNAL'] = node_features['WEB_CONN']
            else:
                node_features['EXTERNAL'] = self._file_is_external(
                    node['uuid'], node['timestamp']
                )

            if self._verbose:
                cnt_done += 1

                x = int(float(cnt_done/ total)*100)

                if x-last_step >= PROGRESS_REPORT['step']:
                    while x >= last_step:
                        last_step += PROGRESS_REPORT['step']
                    last_step -= PROGRESS_REPORT['step']
                    print(PROGRESS_REPORT[last_step/100] % (cnt_done, total))

            result.append({
                'id': (node['uuid'], node['timestamp'],),
                'self': node_features
            })

        return result

    def get_neighbours(self):
        """
            Method that returns a list of the neighbouring nodes for each
            of the nodes provided

        :return:    A list of neighbours for every node.
        """
        result = list()
        if self._verbose:
            cnt_done = 0
            total = len(self._nodes)
            last_step = 0
            print("Getting neibourhood data...")
            print(PROGRESS_REPORT[last_step] % (cnt_done, total))

        for node in self._nodes:

            if any(node[x] is None for x in node):
                continue

            neighs = self._get_neighbours_for_node(
                uuid=node['uuid'],
                timestamp=node['timestamp']
            )

            result.append({
                'id': (node['uuid'], node['timestamp'],),
                'neighs': neighs
            })

            if self._verbose:
                cnt_done += 1

                x = int(float(cnt_done/ total)*100)

                if x-last_step >= PROGRESS_REPORT['step']:
                    while x >= last_step:
                        last_step += PROGRESS_REPORT['step']
                    last_step -= PROGRESS_REPORT['step']
                    print(PROGRESS_REPORT[last_step/100] % (cnt_done, total))

        return result
