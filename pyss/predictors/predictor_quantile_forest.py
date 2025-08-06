from .predictor import Predictor

class PredictorQuantileForest(Predictor):
    """
    estimate_runtime = predict off quantile forest ml
    """

    def __init__(self, options):
        # do anything necessary that will require inits, 
        # so like creating the quantile forest model and selecting interval
        pass
    
    def predict(self, job, current_time, list_running_jobs):
        print(job, type(job))
        exit()
        pass

    def fit(self, job, current_time):
        pass