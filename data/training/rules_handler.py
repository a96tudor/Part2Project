from data.training import constants as cnts
from data.training.database_driver import DatabaseDriver
import pandas as pd

class RulesHandler:

    def __init__(self, db_driver: DatabaseDriver):
        """
                    CONSTRUCTOR

        :param db_driver:       The db driver used to make queries
        """
        self._DB_DRIVER = db_driver
        self._LABEL_1_IDS = set()  # The set of IDs that are a '1' in the training set

    def _get_version_number(self, uuid: str, timestamp: int):
        """

        :param uuid:        The unique ID of the node we want to find the version number for
        :param timestamp:   The timestamp of the current node version

        :return:            The version number, as an integer
        """
        query = 'match (x {uuid: "' + uuid + '"})' \
                    'where x.timestamp < '+ str(timestamp) +' ' \
                'return x.timestamp order by x.timestamp'

        previous_timestamps = self._DB_DRIVER.execute_query(query)

        return len(previous_timestamps)

    def _file_is_from_the_web(self, uuid: str, timestamp: int):
        """

                Method that checks if a given file was downloaded/ edited by a process connected to a different
            machine or if a previous version of this file was downloaded/ edited by a process connected to a different
            machine.

        :param uuid:            The unique ID of the file
        :param timestamp:       The timestamp of the file version

        :return:                1 - if from the web
                                0 - otherwise
        """
        query = 'match (f:File {uuid: "' + uuid + '"})-[fp:PROC_OBJ]->(p:Process)<-[sp:PROC_OBJ]-(s:Socket)' \
                    'where f.timestamp <= ' + str(timestamp) + ' and ' \
                            '(fp.state="WRITE" or fp.state="RaW" or fp.state="NONE") and ' \
                            '(sp.state="CLIENT" or fp.state="RaW") and ' \
                            'not s.name[0]=~"127.0.0.1.*"' \
                'return f.uuid'

        results = self._DB_DRIVER.execute_query(query)

        return 1 if len(results) != 0 else 0

    def _process_is_connected(self, uuid: str, timestamp: int):
        """
            Method that finds out whether a Process is connected to an external machine

        :param uuid:            the unique ID of the process in question
        :param timestamp:       the timestamp used to identify the specific version we're looking for

        :return:                1 - if it connects to a different machine
                                0 - otherwise
        """
        query = 'match (p:Process {uuid: "' + uuid + '", timestamp:"' + str(timestamp) + '"})-[:PROC_OBJ]->(s:Socket)' \
                    ' where not s.name[0]=~"127.0.0.1.*" ' \
                'return s.uuid'

        results = self._DB_DRIVER.execute_query(query)

        return 1 if len(results) > 0 else 0

    def _file_get_closest_process(self, uuid: str, timestamp: int):
        """

                Method that gets the closest Process (i.e. based on the timestamp)

        :param uuid:            Unique ID of the process
        :param timestamp:       Used to identify a specific version of the file

        :return:                A dictionary with the format:
                                {
                                    "uuid":         unique ID of the identified process,
                                    "timestamp":    timestamp of the identified process,
                                    "rel_sts":      type of the edge connecting them
                                }

                                Or None if no such Process
        """
        query = "match (f:File {uuid: '" + uuid + "', timestamp: " + str(timestamp) + "})-[rel:PROC_OBJ]->(p:Process) " \
                "return p.uuid as uuid, " \
                        "p.timestamp as timestamp, " \
                        "rel.state as rel_sts " \
                    "order by abs(p.timestamp-f.timestamp) limit 1"

        results = self._DB_DRIVER.execute_query(query)

        if len(results) == 0:
            return None

        return results[0]

    def _socket_get_closest_process(self, uuid: str, timestamp: int):
        """

                        Method that gets the closest Process (i.e. based on the timestamp)

        :param uuid:            Unique ID of the process
        :param timestamp:       Used to identify a specific version of the file

        :return:                A dictionary with the format:
                                {
                                       "uuid":         unique ID of the identified process,
                                        "timestamp":    timestamp of the identified process,
                                        "rel_sts":      type of the edge connecting them
                                }

                                Or None if no such Process
        """

        query = "match (s:Socket {uuid: '" + uuid + "', timestamp: " + str(timestamp) + "})-[rel:PROC_OBJ]->(p:Process) " \
                "return p.uuid as uuid, " \
                        "p.timestamp as timestamp, " \
                        "rel.state as rel_sts " \
                    "order by abs(p.timestamp-s.timestamp) limit 1"

        results = self._DB_DRIVER.execute_query(query)

        if len(results) == 0:
            return None

        return results[0]

    def _process_get_closest_neighbour(self, p_uuid: str, p_timestamp: int):
        """

                    Method returning the data for the BIN file of a given process

        :param p_uuid:      The ID of the process we want to get the BIN file for
        :param p_timestamp: The timestamp of the process we want to get the BIN file for
        :return:            A dict with the following structure:
                                {
                                    'type': Type of node. Can be either File or Socket
                                    'uuid': Unique ID of the neighbour
                                    'timestamp': Timestamp of the neighbour,
                                    'rel_sts': <Whether the corresponding file was downloaded from the web>
                                }
        """
        query_file = 'match (f:File)-[rel:PROC_OBJ]->(p:Process {uuid: "' + p_uuid + '", ' \
                                                            'timestamp: ' + str(p_timestamp) + '})' \
                'return f.uuid as uuid, f.timestamp as timestamp, rel.state as rel_sts, ' \
                            'abs(f.timestamp - p.timestamp) as diff' \
                    'order by abs(f.timestamp - p.timestamp) limit 1'

        query_socket = 'match (s:Socket)-[rel:PROC_OBJ]->(p:Process {uuid: "' + p_uuid + '", ' \
                                                            'timestamp: ' + str(p_timestamp) + '})' \
                'return s.uuid as uuid, s.timestamp as timestamp, rel.state as rel_sts, ' \
                            'abs(s.timestamp - p.timestamp) as diff' \
                    'order by abs(s.timestamp - p.timestamp) limit 1'

        closest_file = self._DB_DRIVER.execute_query(query_file)
        closest_socket = self._DB_DRIVER.execute_query(query_socket)

        if len(closest_file) == 0 and len(closest_socket) == 0:
            return None

        if len(closest_file) == 0:
            return {
                'uuid': closest_socket[0]['uuid'],
                'timestamp': closest_socket[0]['timestamp'],
                'rel_sts': closest_socket[0]['rel_sts'],
                'type': 'Socket'
            }

        if len(closest_socket) == 0:
            return {
                'uuid': closest_file[0]['uuid'],
                'timestamp': closest_file[0]['timestamp'],
                'rel_sts': closest_file[0]['rel_sts'],
                'type': 'File'
            }

        return {
          'uuid': closest_file[0]['uuid']
                    if closest_file[0]['diff'] < closest_socket[0]['diff']
                    else closest_socket[0]['uuid'],

          'timestamp': closest_file[0]['timestamp']
                        if closest_file[0]['diff'] < closest_socket[0]['diff']
                        else closest_socket[0]['timestamp'],

          'rel_sts': closest_file[0]['uuid'] if closest_file[0]['diff'] < closest_socket[0]['diff'] else
            closest_socket[0]['uuid'],

          'type': 'File' if closest_file[0]['diff'] < closest_socket[0]['diff'] else 'Socket'
        }

    def _file_is_suspicious(self, uuid:str, timestamp: int):
        """

        :param uuid:            The unique ID of the file in question
        :param timestamp:       The timestamp that identifies the file version

        :return:                1 - if suspicious
                                0 - otherwise
        """
        query = 'match (f:File {uuid: "' + uuid+ '", timestamp: ' + str(timestamp) + '}) ' \
                'return f.name'

        name = self._DB_DRIVER.execute_query(query)[0]['f.name']

        if name is None:
            return 0
        else:
            name = name[0]

        if any(sub_str in name for sub_str in cnts.BLACKLIST['File']):
            return 1
        else:
            return 0

    def _process_is_suspicious(self, uuid: str, timestamp: int):
        """

        :param uuid:            The id of the process in question
        :param timestamp:       The timestamp of the process version

        :return:                1 - if it is suspicious
                                0 - otherwise
        """
        query = 'match (p:Process {uuid: "' + uuid + '", timestamp: ' + str(timestamp) + '}) ' \
                'return p.cmdline'

        cmdline = self._DB_DRIVER.execute_query(query)[0]['p.cmdline']

        if any(sub_str in cmdline for sub_str in cnts.BLACKLIST['Process']):
            return 1

        # Otherwise, we need to check if it writes to any file in a location that is not safe,
        # or if the file acting as its binary is on the blacklist
        query = 'match (p:Process {uuid: "' + uuid + '", timestamp: ' + str(timestamp) + '})<-[rel:PROC_OBJ]-(f:File) ' \
                'return rel.state, f.name, f.uuid, f.timestamp'

        q_results = self._DB_DRIVER.execute_query(query)

        for result in q_results:
            if result['rel.state'] == 'BIN' and self._file_is_suspicious(result['f.uuid'], result['f.timestamp']):
                return 1
            if result['rel.state'] != 'READ':
                if any(sub_str in result['f.name'] for sub_str in cnts.DANGEROUS_LOCATIONS):
                    return 1

        # If we've gone through the entire list of files connected to the process in question,
        # and nothing suspicious was identified, we then the process doesn't need the 'suspicious' flag to be set

        return 0

    def _file_is_external(self, uuid: str, timestamp: int):
        """
                Method that checks if a file is external (i.e. whether its
            contents are transmitted via a Socket to a different machine)

        :param uuid:            The unique ID of the file in question
        :param timestamp:       Used to identify the given version of the file

        :return:                1 - if external
                                0 - otherwise
        """
        query = 'match (f:File {uuid: "' + uuid + '", timestamp: ' + str(timestamp) + '})-' \
                        '[rel_fp:PROC_OBJ]->(p:Process)<-[rel_sp:PROC_OBJ]-(s:Socket) ' \
                    'where rel_fp.state <> "BIN" ' \
                'return f.uuid'

        results = self._DB_DRIVER.execute_query(query)

        return 1 if len(results) != 0 else 0

    def _get_process_IDs_status(self, uuid: str, timestamp: int):
        """
                Checks if, for a given process, uid == euid and gid == egid

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

        results = self._DB_DRIVER.execute_query(query)

        return 1 if results[0]['uid_sts'] else 0, \
               1 if results[0]['gid_sts'] else 0

    def _socket_is_external(self, uuid: str, timestamp: int):
        """
                    Method that checks whether a given Socket connects to a different machine or not

        :param uuid:                ID of the Socket in question
        :param timestamp:           Timestamp representing a given version of the Socket

        :return:                    1 - if external
                                    0 - otherwise
        """

        query = 'match (s:Socket {uuid: "' + uuid + '", timestamp: ' + str(timestamp) + '}) ' \
                'return not s.name[0]=~"127.0.0.1.*" as external'

        result = self._DB_DRIVER.execute_query(query)

        if len(result) == 0:
            return 0

        if result[0]['external']:
            return 1
        else:
            return 0

    def _get_all_nodes(self):
        """
            Method that returns all the nodes in the database, excluding: 'Machine', 'Meta' and 'Pipe' nodes

        :return:        {
                            "File":         List of dictionaries containing the return values of the query,
                            "Process":      List of dictionaries containing the return values of the query,
                            "Socket":       List of dictionaries containing the return values of the query
                        }
        """
        query_file = 'match (f: File) ' \
                     'return f.uuid as uuid, f.timestamp as timestamp'

        query_process = 'match (p:Process) ' \
                        'return p.uuid as uuid, p.timestamp as timestamp'

        query_socket = 'match (s:Socket) ' \
                       'return s.uuid as uuid, s.timestamp as timestamp'

        return {
            "File": self._DB_DRIVER.execute_query(query_file),
            "Process": self._DB_DRIVER.execute_query(query_process),
            "Socket": self._DB_DRIVER.execute_query(query_socket)
        }

    def _get_0_row(self, node: dict, neighbour: dict):
        """

        :param node:            The current node. Needs to have the following format:
                                {
                                    'type': The type of node. Can be either File, Process or Socket,
                                    'uuid': Unique ID of the node,
                                    'timestamp': Timestamp of the node version
                                }
        :param neighbour:       The neighbour. Same format as 'node', but with a new key: 'rel_sts'

        :return:                A dictionary, representing a new row in the training set
        """

        check_if_connected = {
            'File': self._file_is_from_the_web,
            'Process': self._process_is_connected,
            'Socket': self._socket_is_external
        }

        check_if_suspicious = {
            'File': self._file_is_suspicious,
            'Process': self._process_is_suspicious
        }

        check_if_external = {
            'File': self._file_is_external,
            'Process': self._process_is_connected,
            'Socket': self._socket_is_external
        }

        if node['type'] == 'Process':
            uid_sts, gid_sts = self._get_process_IDs_status(node['uuid'], node['timestamp'])
        else:
            uid_sts, gid_sts = self._get_process_IDs_status(neighbour['uuid'], neighbour['timestamp'])

        return {
            cnts.FEATURES[0]: node['uuid'],
            cnts.FEATURES[1]: node['timestamp'],
            cnts.FEATURES[2]: cnts.NODE_EDGE_CODES[node['type']]['code'],
            cnts.FEATURES[3]: cnts.NODE_EDGE_CODES[neighbour['type']]['code'],
            cnts.FEATURES[4]: cnts.NODE_EDGE_CODES[node['type']][neighbour['rel_sts']],
            cnts.FEATURES[5]: check_if_connected[node['type']](node['uuid'], node['timestamp']),
            cnts.FEATURES[6]: check_if_connected[neighbour['type']](neighbour['uuid'], neighbour['timestamp']),
            cnts.FEATURES[7]: uid_sts,
            cnts.FEATURES[8]: gid_sts,
            cnts.FEATURES[9]: self._get_version_number(node['uuid'], node['timestamp']),
            cnts.FEATURES[10]: self._process_is_suspicious(neighbour['uuid'], neighbour['timestamp'])
                                    if node['type'] == 'Socket'
                                    else check_if_suspicious[node['type']](node['uuid'], node['timestamp']),
            cnts.FEATURES[11]: check_if_external[node['type']](node['uuid'], node['timestamp']),
            cnts.FEATURES[12]: 0        # They are 0-labeled
        }

    def get_entries_rule_1(self, results: list):
        """
                    Method that build up the new entries for rule #1

        :param results:         A list of dicts containing the results of running the rule1 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """

        rows_list = list()

        for result in results:
            uid_sts, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['f_uuid'],
                cnts.FEATURES[1]: result['f_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['File']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['File']['BIN'],
                cnts.FEATURES[5]: 1,                                       # The rule defines it as being from the web
                cnts.FEATURES[6]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[10]: self._file_is_suspicious(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[11]: self._file_is_external(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[12]: 1
            }
            self._LABEL_1_IDS.add((result['f_uuid'], result['f_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_2(self, results: list):
        """
                    Method that build up the new entries for rule #2

        :param results:         A list of dicts containing the results of running the rule1 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """
        rows_list = list()
        for result in results:
            uid_sts, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['p_uuid'],
                cnts.FEATURES[1]: result['p_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['Socket']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Socket'][result['rel_sts']],
                cnts.FEATURES[5]: 1,  # Defined by the rule itself
                cnts.FEATURES[6]: 1,  # Defined by the rule itself
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[10]: self._process_is_suspicious(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[11]: 1,  # Again, as defined by the rule itself
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['p_uuid'], result['p_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_3(self, results: list):
        """
                    Method that build up the new entries for rule #3

        :param results:         A list of dicts containing the results of running the rule3 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """
        rows_list = list()

        for result in results:
            uid_sts, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['s_uuid'],
                cnts.FEATURES[1]: result['s_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['Socket']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Process'][result['rel_sts']],
                cnts.FEATURES[5]: 1,  # Defined by the rule itself
                cnts.FEATURES[6]: 1,  # Defined by the rule itself
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['s_uuid'], result['s_timestamp']),
                cnts.FEATURES[10]: self._process_is_suspicious(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[11]: 1,  # Again, as defined by the rule itself
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['s_uuid'], result['s_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_4(self, results: list):
        """
                    Method that build up the new entries for rule #4

        :param results:         A list of dicts containing the results of running the rule4 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """

        print(len(results))
        rows_list = list()

        for result in results:
            uid_sts, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['f_uuid'],
                cnts.FEATURES[1]: result['f_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['File']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Process'][result['rel_sts']],
                cnts.FEATURES[5]: self._file_is_from_the_web(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[6]: 1,  # Defined by the rule itself
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[10]: self._process_is_suspicious(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[11]: 1,  # Again, as defined by the rule itself
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['f_uuid'], result['f_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_5(self, results: list):
        """
                    Method that build up the new entries for rule #5

        :param results:         A list of dicts containing the results of running the rule5 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """
        rows_list = list()

        for result in results:
            _, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['p_uuid'],
                cnts.FEATURES[1]: result['p_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['File']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Process']['BIN'],
                cnts.FEATURES[5]: self._file_is_from_the_web(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[6]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[7]: 0,  # As defined by the rule itself
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[10]: self._process_is_suspicious(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[11]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['p_uuid'], result['p_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_8(self, results: list):
        """
                    Method that build up the new entries for rule #8

        :param results:         A list of dicts containing the results of running the rule8 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """
        rows_list = list()

        for result in results:
            uid_sts, _ = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['p_uuid'],
                cnts.FEATURES[1]: result['p_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['File']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Process']['BIN'],
                cnts.FEATURES[5]: self._file_is_from_the_web(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[6]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: 1, # As defined by the rule itself
                cnts.FEATURES[9]: self._get_version_number(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[10]: self._process_is_suspicious(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[11]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['p_uuid'], result['p_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_9(self, results: list):
        """
                            Method that build up the new entries for rule #9

        :param results:         A list of dicts containing the results of running the rule9 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """
        rows_list = list()

        for result in results:
            uid_sts, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['p_uuid'],
                cnts.FEATURES[1]: result['p_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['File']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Process']['BIN'],
                cnts.FEATURES[5]: self._file_is_from_the_web(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[6]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[10]: 1,  # As defined by the rule
                cnts.FEATURES[11]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['p_uuid'], result['p_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_10(self, results: list):
        """
                            Method that build up the new entries for rule #8

        :param results:         A list of dicts containing the results of running the rule8 cypher statement
        :return:                A pd.Dataframe containing all required entries
        """
        rows_list = list()

        for result in results:
            uid_sts, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['p_uuid'],
                cnts.FEATURES[1]: result['p_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['File']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Process'][result['rel_sts']],
                cnts.FEATURES[5]: self._file_is_from_the_web(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[6]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[10]: 1,  # As defined by the rule itself
                cnts.FEATURES[11]: self._process_is_connected(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['p_uuid'], result['p_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_entries_rule_14(self, results: list):
        """
                                    Method that build up the new entries for rule #8

                :param results:         A list of dicts containing the results of running the rule8 cypher statement
                :return:                A pd.Dataframe containing all required entries
                """
        print(len(results))
        rows_list = list()

        for result in results:
            uid_sts, gid_sts = self._get_process_IDs_status(result['p_uuid'], result['p_timestamp'])
            new_row = {
                cnts.FEATURES[0]: result['p_uuid'],
                cnts.FEATURES[1]: result['p_timestamp'],
                cnts.FEATURES[2]: cnts.NODE_EDGE_CODES['Process']['code'],
                cnts.FEATURES[3]: cnts.NODE_EDGE_CODES['File']['code'],
                cnts.FEATURES[4]: cnts.NODE_EDGE_CODES['Process'][result['rel_sts']],
                cnts.FEATURES[5]: self._file_is_from_the_web(result['f_uuid'], result['f_timestamp']),
                cnts.FEATURES[6]: 1,  # As defined by the rule
                cnts.FEATURES[7]: uid_sts,
                cnts.FEATURES[8]: gid_sts,
                cnts.FEATURES[9]: self._get_version_number(result['p_uuid'], result['p_timestamp']),
                cnts.FEATURES[10]: 1,  # As defined by the rule
                cnts.FEATURES[11]: 1,  # As defined by the rule
                cnts.FEATURES[12]: 1
            }

            self._LABEL_1_IDS.add((result['p_uuid'], result['p_timestamp']))

            rows_list.append(new_row)

        return pd.DataFrame(rows_list)

    def get_0_labels(self):
        """
            Method that gets the nodes '0' labels

        :return:        A pd.Dataframe with the '0'-labeled nodes
        """
        all_rows = list()

        all_nodes = self._get_all_nodes()

        for file in all_nodes['File']:

            if (file['uuid'], file['timestamp']) in self._LABEL_1_IDS:
                # We already entered this node as a 'label 1' in the training set, so we skip it
                continue

            if file['uuid'] is None or file['timestamp'] is None:
                continue

            process = self._file_get_closest_process(file['uuid'], file['timestamp'])

            if process is None:
                # Just ignore this entry, too
                continue

            process['type'] = 'Process'
            file['type'] = 'File'

            all_rows.append(
                self._get_0_row(
                    node=file,
                    neighbour=process
                )
            )

        for socket in all_nodes['Socket']:

            if (socket['uuid'], socket['timestamp']) in self._LABEL_1_IDS:
                # We already entered this node as a 'label 1' in the training set, so we skip it
                continue

            if socket['uuid'] is None or socket['timestamp'] is None:
                continue

            process = self._socket_get_closest_process(socket['uuid'], socket['timestamp'])

            if process is None:
                # Just ignore this entry
                continue

            process['type'] = 'Process'
            socket['type'] = 'Socket'

            all_rows.append(
                self._get_0_row(
                    node=socket,
                    neighbour=process
                )
            )

        for process in all_nodes['Process']:

            if (process['uuid'], process['timestamp']) in self._LABEL_1_IDS:
                # We already entered this node as a 'label 1' in the training set, so we skip it
                continue

            if process['uuid'] is None or process['timestamp'] is None:
                continue

            closest_node = self._process_get_closest_neighbour(process['uuid'], process['timestamp'])

            if closest_node is None:
                # Just ignore this entry
                continue

            process['type'] = 'Process'

            all_rows.append(
                self._get_0_row(
                    node=process,
                    neighbour=closest_node
                )
            )

        return pd.DataFrame(all_rows)

    def get_1_labeled_count(self):
        """
                Method that returns the count of nodes 1-labeled

        :return:        The number of 1-labeled nodes
        """
        return len(self._LABEL_1_IDS)
