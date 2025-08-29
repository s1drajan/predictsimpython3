from .predictor import Predictor
from pyss.base import job_types

from quantile_forest import RandomForestQuantileRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn import feature_selection

import pandas as pd
import time

TRAIN_MAX = 5000

"""
Each application gets there own Controller which wraps the necessary logic and functions
"""
class Controller():
    def __init__(self): 
        self.model = RandomForestQuantileRegressor()
        self.df = pd.DataFrame()
        self.is_trained = False

    def concat(self, new_df):
        self.df = pd.concat([self.df, new_df], ignore_index=True)

    def transform_df(self, predictCol):
        X = self.df
        y = self.df[predictCol]

        # replacements for base cases - can abstract later for more control if we need it
        X = X.replace('on', '1', regex=True)
        X = X.replace('off', '0', regex=True)
        X = X.replace('true', '1', regex=True)
        X = X.replace('false', '0', regex=True)
        X = X.replace('.true.', '1', regex=True)
        X = X.replace('.false.', '0', regex=True)

        X = X.drop(columns=predictCol)

        return X,y
    
    def generate_preprocessor(self, X):
        numeric_features = []
        categorical_features = []
        # X = self.df # to adapt to the copied code
    
        for col in X:
            # Identify what type each column is.
            isNumeric = True
            for rowIndex, row in X[col].items():
                try:
                    # If it can be a float, make it a float.
                    X.loc[col][rowIndex] = float(X.loc[col][rowIndex])
                    # If the float is NaN (unacceptable to Sci-kit), make it -1.0 for now.
                    if pd.isnull(X[col][rowIndex]):
                        X.loc[col][rowIndex] = -1.0
                except:
                    # Otherwise, we will assume this is categorical data.
                    isNumeric = False
            if isNumeric:
                # For whatever reason, float conversions don't want to work in Pandas dataframes.
                # Try changing the value column-wide instead.
                # TODO: Doesn't seem to actually solve anything.
                X.loc[col] = X.loc[col].astype(float)
                numeric_features.append(str(col))
            else:
                categorical_features.append(str(col))

        # Standardization for numeric data.
        numeric_transformer = Pipeline(
            steps=[("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())])

        # One-hot encoding for categorical data.
        categorical_transformer = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        # Add the transformers to a preprocessor object.
        preprocessor = ColumnTransformer(transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),])

        return preprocessor
    
    def get_pipeline(self, preprocessor, clf):
        """ 
        Convenience function to add a preprocessor to a regression pipeline.
        """
        return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])

    def get_regressor(self,X):
        preprocessor = self.generate_preprocessor(X)
        return self.get_pipeline(preprocessor, self.model)
    
    def train(self,X,y):
        if self.is_trained:
            print("WARNING ATTEMPTING TO TRAIN A MODEL WHICH IS ALREADY TRAINED...")
            return 

        regressor = self.get_regressor(X)

        startTime = time.process_time()
        self.regressor = regressor.fit(X, y)
        endTime = time.process_time()

        # finishing the training
        self.is_trained = True
    
    def predict(self,x):
        if not self.regressor or not self.is_trained:
            print("WARNING WE HAVE NO REGRESSOR TO PREDICT On")
            exit()
        
        return self.regressor.predict(x,quantiles=[0.5,0.6,0.7])
    
    @property
    def df_rows(self):
        return self.df.shape[0]

class PredictorQuantileForest(Predictor):
    """
    estimate_runtime = predict off quantile forest ml
    """
    def __init__(self, options):
        # do anything necessary that will require inits, 
        # so like creating the quantile forest model and selecting interval 
        self.controllers = {}
        self.t = 0

        for job_type in job_types.JOB_TYPE_RANGE:
            self.controllers[job_type] = Controller()

        pass
    
    def predict(self, job, current_time, list_running_jobs):
        # when we start prediction follow this algorithm
        # P = quant.predict(), if P > requested_time: requested_time else P
        # maybe some methodogly could be used that if we our under a specfic runtime then we shouldn't predict
        controller = self.controllers[job.job_type]

        if not controller.is_trained:
            job.predicted_run_time = job.user_estimated_run_time
            return
        
        print(controller.predict(pd.DataFrame([job.input_params])), job.actual_run_time)
        exit()

    """
    This function will be used to train and retrain the model

    For now we will just implement the intital train (5000 jobs) and worry about retraining later
    """
    def fit(self, job, current_time):
        controller = self.controllers[job.job_type]

        if controller.df_rows < TRAIN_MAX:
            job.input_params["timeTaken"] = job.actual_run_time # save real runtime so we can train on it
            controller.concat(pd.DataFrame([job.input_params]))
            return 

        if controller.is_trained:
            return

        # controller not trained and we have enough TRAIN data 
        print('starting train')
        # temp code to verify dataframe
        controller.df.to_csv(f"results/job-{job_types.JOB_TYPE_TO_STR[job.job_type]}-out.csv")

        X,y = controller.transform_df(predictCol="timeTaken")
        controller.train(X,y)