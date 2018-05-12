"""
Part2Project -- config.py

Copyright Mar 2018 [Tudor Mihai Avram]

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
from models.evaluation import metrics
from data.features import constants


class ModelConfig(object):
    """
        'Mother' class for model configuration
    """
    CHECKPOINTS_PATH = "models/checkpoints/"

    LABELS = constants.LABELS
    FEATURES = constants.FEATURES_ONE_HOT


class TrainConfig(ModelConfig):
    """
        Configuration class for the training mode
    """
    DATA_PATH = 'data/training/training-set.csv'
    SHUFFLE = False  # If we want to shuffle the dataset. Useful for evaluation
    NORMALIZE = True  # We want to normalize the data first.



class EvalConfig(ModelConfig):
    """
        Configuration class for the evaluation mode
    """
    DATA_PATH = 'data/training/training-set.csv'
    SHUFFLE = True  # We want to shuffle the data first to get more accurate results
    NORMALIZE = True  # We want to normalize the data first
    METRICS = {
        "accuracy": metrics.accuracy,
        "mcc": metrics.mcc,
        "f1": metrics.f1,
        "tp": metrics.true_positives,
        "tn": metrics.true_negatives,
        "fp": metrics.false_positives,
        "fn": metrics.false_negatives,
        "precision": metrics.precision,
        "recall": metrics.recall
    }
    RESULTS_PATH = 'models/eval/results/'
    THRESHOLD = .5  # Probability above which we want to classify the node as 'SHOW'


class PredictConfig(ModelConfig):
    """
        Configuration class for prediction mode
    """
    FEATURE_EXTRACTOR = {
        'NODE_TYPE': None,
        'NEIGH_TYPE': None,
        'EDGE_TYPE': None,
        'WEB_CONN': None,
        'NEIGH_WEB_CONN': None,
        'UID_STS': None,
        'GID_STS': None,
        'VERSION': None,
        'SUSPICIOUS': None,
        'EXTERNAL': None
    }
    THRESHOLD = .5  # Probability above which we want to classify the node as 'SHOW'
