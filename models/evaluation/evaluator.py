from models.model import Model
from datetime import datetime as dt
import os

class Evaluator(object):
    """
        Skeleton class for an evaluator
    """

    def __init__(self, model: Model, data_path: str):
        """

        :param model:               The model that we want to evaluate
        :param data_path:           Path to the dataset we're using for evaluation
        """
        self._model = model
        self._data_path = data_path
        self._results = {
            "model": str(self._model),
            "date": str(dt.now())
        }
        self._result_path = self._get_result_file_path()

        print("===================== STARTED EVALUATION ===============================")
        print("   Date: %s" % self._results['date'])
        print("   Model: %s" % str(self._model))
        print("   Results saved in: %s" % self._result_path)

    def get_results(self):
        """

        :return:            The results of the evaluation
        """
        return self._results

    def _get_result_file_path(self):
        """
            The default value for saving the results is models/evaluation/results/<self._model>/<x>.json,
            where x is just a local ID for those specific results

        :return:
        """
        if not os.path.isdir('models/evaluation/results'):
            os.makedirs('models/evaluation/results')

        if not os.path.isdir('models/evaluation/results/%s' % str(self._model)):
            os.makedirs('models/evaluation/results/%s' % str(self._model))

        files = os.listdir('models/evaluation/results/%s' % str(self._model))
        max_in_count = 0

        for file in files:
            try:
                count = int(file.split('.')[0])
                max_in_count = max(max_in_count, count)
            except:
                continue

        return 'models/evaluation/results/%s/%d.json' % (str(self._model), max_in_count+1)
