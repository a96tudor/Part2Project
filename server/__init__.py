from flask import Flask, request, Response, jsonify
#from server.config import Config
from server.cache import CacheHandler
from data.neo4J.database_driver import AnotherDatabaseDriver
from models import get_model
from models.config import PredictConfig

from server.views import *
from server import utils


class API(Flask):
    """
        Class represening REST API
    """
    def __init__(self,
                 include_name,
                 config,
                 *args,
                 **kwargs):
        """

        :param include_name:    The name of the environment the API is run in
        :param config:          The config the API is run in
        :param args:            other arguments
        :param kwargs:          other arguments
        """

        super(API, self).__init__(include_name, *args, **kwargs)

        # Adding the rules from the config
        for view in config.views:
            self.add_url_rule(
                view['url'],
                view_func=view['class'].as_view(view['url'])
            )

        self.cacheConnData = config.CACHE_CONN_DATA

        utils.cacheHandler = CacheHandler(
            user=self.cacheConnData['user'],
            password=self.cacheConnData['password'],
            host=self.cacheConnData['host'],
            port=self.cacheConnData['port'],
            dbName=self.cacheConnData['dbName']
        )

        utils.jobsHandler = JobsHandler(
            cacheConnData=config.CACHE_CONN_DATA,
            neo4jConnData=config.NEO4J_CONN_DATA,
            defaultTTL=config.TTL,
            defaultModel=config.MODEL
        )

        utils.model = get_model(
            name=config.MODEL['name'],
            config=PredictConfig,
            checkpoint=config.MODEL['checkpoint']
        )
