from flask import Flask, request, Response, jsonify


def get_app(config_name):
    """
    :param config_name:     Type of configuration wanted for the REST API.
                            Has to be one of: 'development', 'testing',
                                              'staging', 'production'
    :return:
    """
    return None