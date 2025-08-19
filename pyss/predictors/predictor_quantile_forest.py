from .predictor import Predictor
from pyss.base import job_types
from quantile_forest import RandomForestQuantileRegressor

class PredictorQuantileForest(Predictor):
    """
    estimate_runtime = predict off quantile forest ml
    """
    def __init__(self, options):
        # do anything necessary that will require inits, 
        # so like creating the quantile forest model and selecting interval 
        self.models = {}
        for job_t in job_types.JOB_TYPE_RANGE:
            self.models[job_t] = RandomForestQuantileRegressor()
        pass
    
    def predict(self, job, current_time, list_running_jobs):
        print(job, type(job))
        exit()
        pass

    def fit(self, job, current_time):
        pass