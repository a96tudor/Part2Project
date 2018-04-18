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

        :param name:
        """
        super(API, self).__init__(include_name, *args, **kwargs)
        """
        for view in config.views:
            self.add_url_rule(
                view['url'],
                view['class']
            )
        """
        self.add_url_rule('/classify',
                          view_func=ClassifyView.as_view('classify_view'))
