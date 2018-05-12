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
from data.features.feature_extractor import FeatureExtractor
from data.neo4J.database_driver import AnotherDatabaseDriver
from server.cache import CacheHandler
from datetime import datetime as dt
from numpy import random
import base64
from server import utils


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

    def run(self):
        """

        :return:    -
        """
        self.status = 'RUNNING'
        self.cacheHandler.update_job_status(
            self.jobID,
            self.status
        )

        self.featureExtractor = FeatureExtractor(
            nodes=self.nodes,
            verbose=True,
            driver=self.neo4jDriver
        )

        feature_vectors = self.featureExtractor.get_feature_matrix()




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




