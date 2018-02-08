from models.logistic_regression import LogisticRegression

_STR_TO_MODEL = {
    "logistic": LogisticRegression
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

    model = _STR_TO_MODEL[model_name](
        train_path=paths[0],
        test_path=paths[1],
        log=log
    )

    model.setup()
