from models.logistic_regression import LogisticRegression
from models.pnn import ProbabilisticNeuralNetwork
import json
from data import utils

_STR_TO_MODEL = {
    "logistic": LogisticRegression,
    "pnn": ProbabilisticNeuralNetwork
}


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

    utils.shuffle_csv(path)

    results = dict()

    for idx in range(int(100/25) - 1):
        results[idx] = model.evaluate()
        print("Iteration: %d" % (idx+1))
        print(results[idx])
        model.renew_split(idx+2)

    path_results = 'data/results/' + model_name + "/1.json"

    with open(path_results, 'w') as fout:
        json.dump(results, fout)
