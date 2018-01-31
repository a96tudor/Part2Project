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

    def _process_get_BIN_file(self, p_uuid: str, p_timestamp: int):
        """

                    Method returning the data for the BIN file of a given process

        :param p_uuid:      The ID of the process we want to get the BIN file for
        :param p_timestamp: The timestamp of the process we want to get the BIN file for
        :return:            A dict with the following structure:
                                {
                                    'NEIGH_TYPE': <The neighbour code>,
                                    'EDGE_TYPE': <The edge code connecting to the neighbour>,
                                    'NEIGH_WEB_CONN': <Whether the corresponding file was downloaded from the web>
                                }
        """
        query = 'match (f:File)-[:PROC_OBJ {state: "BIN"}]->(p:Process {uuid: "' + p_uuid + '", ' \
                                                                        'timestamp: ' + str(p_timestamp) + '})' \
                'return f.uuid, f.timestamp'

        results = self._DB_DRIVER.execute_query(query)

        return {
          'NEIGH_TYPE': cnts.NODE_EDGE_CODES['File']['code'],
          'EDGE_TYPE': cnts.NODE_EDGE_CODES['File']['BIN'],
          'NEIGH_WEB_CONN': self._file_is_from_the_web(
              results[0]['f.uuid'],
              results[0]['f.timestamp']
          )
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