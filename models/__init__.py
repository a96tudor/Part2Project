from models.logistic_regression import LogisticRegression
from data import utils
import pandas as pd
from models.pnn import ProbabilisticNeuralNetwork
import json
from data import utils

_STR_TO_MODEL = {
    "logistic": LogisticRegression,
    "pnn": ProbabilisticNeuralNetwork
}

NUM_ITER = 20


def evaluate(model_name, paths=('data/tmp/train.csv', 'data/tmp/test/csv'), log=False):
    """
    :param model_name:   The model we want to evaluate, as a string
                            It can be:
                                - logistic
    :param paths:       (training_set path, test_test path) touple
    :param log:         Whether we want to log everything
    :return:            -
    """

    path = 'data/training/training_set.csv'

    model = _STR_TO_MODEL[model_name](
        data_path=path,
        evaluate=True
    )

    df = pd.read_csv('data/training/training_set.csv')

    results = dict()

    results['methodology'] = 'Random Cross Validation'
    results['iterations'] = NUM_ITER

    results['metrics'] = dict()

    for idx in range(NUM_ITER):
        results['metrics'][idx] = model.evaluate()
        print("Iteration: %d" % (idx+1))
        model.renew_split(idx+1)
        print(results['metrics'][idx])

    path_results = 'data/results/' + model_name + "/1.json"

    results['summary'] = {
        key: float(sum([results['metrics'][idx][key] for idx in range(NUM_ITER)])/NUM_ITER)
                for key in results['metrics'][0]}

    with open(path_results, 'w') as fout:
        json.dump(results, fout)