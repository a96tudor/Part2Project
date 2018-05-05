"""
Part2Project -- __init__.py.py

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
from data.utils import read_csv, split_dataframe, get_new_filename_in_dir, dump_json
from models.config import *
from models.cnn import ConvolutionalNeuralNetwork
from models.pnn import ProbabilisticNeuralNetwork
from models.mlp import MultilayerPerceptron
from models.logistic_regression import LogisticRegression
from models.gat import GraphAttentionNetwork
from models.model import Model

import numpy as np
import pandas as pd
import abc

_ACCEPTED_MODELS = {
    'cnn': ConvolutionalNeuralNetwork,
    'pnn': ProbabilisticNeuralNetwork,
    'mlp': MultilayerPerceptron,
    'logreg': LogisticRegression,
    'gat': GraphAttentionNetwork
}


def get_model(name: str,
              config: ModelConfig) -> Model:
    """
        Method that initiates and sets up a model, based on
        the model name and the configuration
        the model will be run in.

    :param name:            The name of the model
    :param config:          The configuration the file will be run in

    :return:                The resulting model object
    """

    assert(name in _ACCEPTED_MODELS)

    model = _ACCEPTED_MODELS[name](config)

    model.setup(input_dim=config.INPUT_DIM)

    return model

