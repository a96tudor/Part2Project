from models.evaluation.evaluator import Evaluator
from models.model import Model


class CrossValidationEvaluator(Evaluator):
    """
        Class for a RANDOM splitting CrossValidator
    """

    def __init__(self, model: Model, data_path: str, iterations: int, percentile: float = 0.90):
        """

        :param model:
        :param data_path:
        :param iterations:
        :param percentile:
        """
