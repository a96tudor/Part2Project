from models.logistic_regression import LogisticRegression
from models.pnn import ProbabilisticNeuralNetwork

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

    path = 'data/training/training-set.csv'

    model = _STR_TO_MODEL[model_name](
        data_path=path,
        evaluate=True
    )

    model.setup()
