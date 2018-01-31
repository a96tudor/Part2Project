import data.training.constants as cnts
import pandas as pd

class RulesHandler:

    def __init__(self, db_driver):
        """
                    CONSTRUCTOR

        :param db_driver:       The db driver used to make queries
        """
        self._DB_DRIVER = db_driver
        self._ONES_IDS = set()  # The set of IDs that are a '1' in the training set

    def _get_version_number(self, uuid, timestamp):
        """

        :param uuid:        The unique ID of the node we want to find the version number for
        :param timestamp:   The timestamp of the current node version

        :return:            The version number, as an integer
        """
        query = 'match (p {uuid: "' + uuid + '"})' \
                'return p.timestamp order by p.timestamp'

        all_timestamps = self._DB_DRIVER.execute_query(query)

        all_timestamps = [x['p.timestamp'] for x in all_timestamps]

        try:
            idx = sorted(all_timestamps).index(timestamp)
        except:
            idx = 0

        return idx

    def _file_is_from_the_web(self, uuid, timestamp):
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

    def _process_is_connected(self, uuid, timestamp):
        """

        :param uuid:
        :param timestamp:
        :return:
        """

    def _process_get_BIN_file(self, p_uuid, p_timestamp):
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

    def get_entries_rule_1(self, results):
        """
                    Method that build up the new entries for rule #1

        :param results:         A list of dicts containing the results of running the rule1 cypher statement
        :return:                a pd.Dataframe containing all entries
        """