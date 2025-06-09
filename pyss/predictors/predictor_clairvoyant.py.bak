from .predictor import Predictor


class PredictorClairvoyant(Predictor):
    """
    estimate_runtime = real runtime [* predict_multiplier]
    """

    def __init__(self, options):
        if "predict_multiplier" in options["scheduler"]["predictor"].keys():
            self.predict_multiplier = options["scheduler"]["predictor"]["predict_multiplier"]
        else:
            self.predict_multiplier = 1
        # print(self.predict_multiplier)

    def predict(self, job, current_time, list_running_jobs):
        """
        Modify the predicted_run_time of a job.
        Called when a job is submitted to the system.
        """
        job.predicted_run_time = job.actual_run_time*self.predict_multiplier

    def fit(self, job, current_time):
        """
        Add a job to the learning algorithm.
        Called when a job end.
        """
        pass
