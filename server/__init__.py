from flask import Flask, request, Response, jsonify
#from server.config import Config
from server.views import *

jobsHandler = None
cacheHandler = None
featureExtractor = None


def get_app(config_name):
    """
    :param config_name:     Type of configuration wanted for the REST API.
                            Has to be one of: 'development', 'testing',
                                              'staging', 'production'
    :return:
    """
    return None


class API(Flask):
    """
        Class
    """
    def __init__(self,
                 include_name,
                 config,
                 *args,
                 **kwargs):
        """

        :param include_name:
        :param config:
        :param args:
        :param kwargs:
        """

        super(API, self).__init__(include_name, *args, **kwargs)

        # Adding the rules from the config
        for view in config.views:
            self.add_url_rule(
                view['url'],
                view_func=view['class'].as_view(view['url'])
            )
