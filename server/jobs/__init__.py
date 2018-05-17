"""
Part2Project -- __init__.py

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
from models.model import Model
from data.features import get_dataset, build_df_from_list, get_node_type, get_closest_process, get_df_from_list
from data.features.constants import FEATURES_ONE_HOT
from data.neo4J.database_driver import AnotherDatabaseDriver
from server.cache import CacheHandler
from datetime import datetime as dt
from server.utils import CLASSIFIABLE_NODES, UNCLASSIFIABLE_NODES
from numpy import random
import base64
import numpy as np
import json
from multiprocessing import Process


class RequestJob(object):
    """

    """

    def __init__(self,
                 nodes: list,
                 model: Model,
                 cache_handler: CacheHandler,
                 driver: AnotherDatabaseDriver,
                 jobID: str,
                 ttl: int,
                 batch_size: int):
        """

        :param nodes:
        :param model:
        :param cache_handler:
        :param feature_extractor:
        :param jobID:
        :param ttl:
        """
        self.nodes = nodes
        self.model = model
        self.cacheHandler = cache_handler
        self.neo4jDriver = driver
        self.jobID = jobID
        self.ttl = ttl
        self.batchSize = batch_size
        self.status = 'WAITING'

        self.to_extract = list()

    def _preprocess_on_type(self):
        """

        :return:
        """
        results = list()

        for node in self.nodes:
            type = get_node_type(
                driver=self.neo4jDriver,
                uuid=node['uuid'],
                timestamp=node['timestamp']
            )

            if type in CLASSIFIABLE_NODES:
                self.to_extract.append(node)
            else:
                if type == 'Pipe':
                    uuid, timestamp = get_closest_process(
                        driver=self.neo4jDriver,
                        uuid=node['uuid'],
                        timestamp=node['timestamp']
                    )
                    self.to_extract.append({
                        'uuid': uuid,
                        'timestamp': timestamp
                    })
                elif type == 'Machine':
                    results.append({
                        'uuid': node['uuid'],
                        'timestamp': node['timestamp'],
                        'showProb': 1.0,
                        'hideProb': 0.0,
                        'recommended': 'SHOW'
                    })
                else:
                    results.append({
                        'uuid': node['uuid'],
                        'timestamp': node['timestamp'],
                        'showProb': 0.0,
                        'hideProb': 1.0,
                        'recommended': 'HIDE'
                    })
        return results

    def _get_feature_vectors(self):
        """

        :return:
        """
        raw_feature_vectors = get_dataset(
            driver=self.neo4jDriver,
            nodes=self.to_extract,
            include_NONE=True
        )

        results = list()
        feature_vectors = list()

        for fv in raw_feature_vectors:
            if fv['self'] is None:
                results.append({
                    'uuid': fv['id'][0],
                    'timestamp': fv['id'][1],
                    'showProb': None,
                    'hideProb': None,
                    'recommended': None
                })
                self.to_extract.pop(self.to_extract.index({'uuid': fv['id'][0], 'timestamp': fv['id'][1]}))
            else:
                feature_vectors.append(fv)

        feature_matrix = get_df_from_list(feature_vectors).as_matrix(columns=FEATURES_ONE_HOT)

        return feature_matrix, results

    def _process_probabilities(self,
                               probs: np.ndarray):

        """

        :param probs:
        :return:
        """

        results = list()

        for i in range(len(probs)):
            new_result = self.to_extract[i]
            new_result['showProb'] = probs[i, 0]
            new_result['hideProb'] = probs[i, 1]
            new_result['classifiedBy'] = self.model.name

            if probs[i, 0] >= probs[i, 1]:
                new_result['recommended'] = 'SHOW'
            else:
                new_result['recommended'] = 'HIDE'

            results.append(new_result)

        return results


    def run(self):
        """

        :return:    -
        """
        self.status = 'RUNNING'
        self.cacheHandler.update_job_status(
            self.jobID,
            self.status
        )

        results = self._preprocess_on_type()

        Xs, res = self._get_feature_vectors()

        results += res

        probs = self.model.predict_probs(
            data=Xs
        )

        res = self._process_probabilities(probs)

        results += res

        print(results)


class JobsHandler(object):
    """

    """
    def __init__(self,
                 neo4jConnData: dict,
                 cacheConnData: dict,
                 defaultTTL: int,
                 defaultModel: str):
        """

        :param neo4jConnData:
        :param cacheConnData:
        :param defaultTTL:
        :param defaultModel:
        """
        self.cacheConnData = cacheConnData

        self.defaultModel = defaultModel

        self.defaultTTL = defaultTTL

        self.neo4jConnData = neo4jConnData

    def _generate_jobID(self,
                        nodesCount: int):
        """
            The jobID will be generated as folllows:
                1. generate a string:
                    date of the incoming request || nodesCount || a random set of 5 digits
                2. get the base64 encoding of that string

        :param nodesCount:      Number of nodes in the job
        :return:                The generated jobID
        """
        current_date = str(dt.now()).replace(' ', '').replace('-', '').replace('.', '').replace(':', '')
        rnd_seq = ''.join([str(x) for x in random.choice(9, 5)])

        raw_string = "%s%s" % (current_date, rnd_seq)

        shuffled = "".join(random.sample(raw_string, len(raw_string)))

        b64encoded = base64.encodebytes(bytes(shuffled, 'utf-8'))
        idChars = [str(c) for c in b64encoded][2:-4]
        jobID = "".join(idChars)

        return jobID

    def add_job(self,
                nodes: list,
                ttl=None,
                model=None,
                cacheHandler=None,
                featureExtractor=None):
        """

        :param nodes:
        :param ttl:
        :param model:
        :param cacheHandler:
        :param featureExtractor:
        :return:
        """

        newJobID = self._generate_jobID(len(nodes))

        newJob = RequestJob(
            nodes=nodes,
            model=model if model else self.defaultModel,
            cache_handler=cacheHandler if cacheHandler else self.defaultCacheHandler,
            feature_extractor=featureExtractor if featureExtractor else self.defaultFeatureExtractor,
            jobID=newJobID,
            ttl=self.defaultTTL
        )




