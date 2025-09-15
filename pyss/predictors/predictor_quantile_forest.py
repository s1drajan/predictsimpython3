from .predictor import Predictor
from pyss.base import job_types

from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from quantile_forest import RandomForestQuantileRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn import feature_selection

import pickle
import pandas as pd
import time

import os

WINDOW_MAX = 10000
TRAIN_MAX = 5000
RETRAIN_MAX = 100 # https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7776517

PICKLE_DIR = "./pickles/"
SHOULD_DEPICKLE = False 
SHOULD_PICKLE = False

# helper functions when processing data
def generate_preprocessor(X):
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
        if isNumeric or X[col].dtype == float:
            # For whatever reason, float conversions don't want to work in Pandas dataframes.
            # Try changing the value column-wide instead.
            # TODO: Doesn't seem to actually solve anything.
            # X.loc[col] = X.loc[col].astype(float)
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

def get_pipeline(preprocessor, clf):
    """ 
    Convenience function to add a preprocessor to a regression pipeline.
    """
    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])

class PickleData:
    def __init__(self, train_max, window_max, retrain_max, data):
        self.train_max = train_max
        self.window_max = window_max
        self.retrain_max = retrain_max
        self.data = data
    
    def get_data(self):
        res = (self.train_max, self.window_max, self.retrain_max)
        expected = (TRAIN_MAX, WINDOW_MAX, RETRAIN_MAX)

        if res == expected:
            return self.data
        exit(f"bad pickle - (expected {res}) != (got {expected})")

"""
Each application gets there own Controller which wraps the necessary logic and functions
"""
class Controller():
    def __init__(self, job_type, timestamp_id,
                 quantiles, input_file : str, pickling=False,
                 sliding_window=False, drop_cols=[]): 
        
        # consturctor args
        self.job_type = job_type
        self.drop_cols = drop_cols
        self.quantiles = quantiles 
        self.is_sliding_window = sliding_window
        self.timestamp_id = timestamp_id
        self.pickling = pickling

        # other values written
        self.model = RandomForestQuantileRegressor()
        self.df = pd.DataFrame()
        self.train_batch = pd.DataFrame()


        self.job_type_str = job_types.JOB_TYPE_TO_STR[job_type]
        self.is_trained = False
        self.train_iter = 0

        # pickle_dir/input_file/app_name/*
        self.pickling_dir = f"{PICKLE_DIR}{input_file.split("/")[-1].replace(" ","-")}/{self.job_type_str.replace(" ","-")}/"

    def get_pickle_name(self,train_iter):
        return  f"regressor-{train_iter}-{TRAIN_MAX}-{WINDOW_MAX}-{RETRAIN_MAX}"
    
    def pickle_regressor(self,regressor,train_iter):
        if not SHOULD_PICKLE:
            return 
        
        print("saving regressor ",self.train_iter)

        if not os.path.exists(self.pickling_dir):
            os.makedirs(self.pickling_dir)
        
        pickled_data = PickleData(train_max=TRAIN_MAX,
                   window_max=WINDOW_MAX,
                   retrain_max=RETRAIN_MAX,
                   data=regressor)
        

        pickle.dump(pickled_data, open(self.pickling_dir + self.get_pickle_name(train_iter), 'wb'))

    def depickle_regressor(self,train_iter):
        pickle_data = pickle.load(open(self.pickling_dir + self.get_pickle_name(train_iter), 'rb'))
        return pickle_data.get_data()

    def concat(self, new_df):
        # not sliding window or we aren't ready to trim the window
        if not self.is_sliding_window or self.df.shape[0] < WINDOW_MAX:
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            return
        
        # adjusting train window
        self.df = pd.concat([self.df.iloc[RETRAIN_MAX:],new_df],ignore_index=True)

    def transform_df(self, df, predictCol):
        X = df
        y = df[predictCol]

        # replacements for base cases - can abstract later for more control if we need it
        X = X.replace('on', '1', regex=True)
        X = X.replace('off', '0', regex=True)
        X = X.replace('true', '1', regex=True)
        X = X.replace('false', '0', regex=True)
        X = X.replace('.true.', '1', regex=True)
        X = X.replace('.false.', '0', regex=True)

        X = X.drop(columns=predictCol)

        # drop cols
        for col in self.drop_cols:
            if not col in X.columns:
                # print(f"warning {col} not in dataset, not dropping")
                continue

            X = X.drop(columns=col)

        return X,y 

    def get_regressor(self,X):
        preprocessor = generate_preprocessor(X)
        return get_pipeline(preprocessor, self.model)

    def fit(self, job):
        # save real runtime so we can train on it
        job.input_params["timeTaken"] = job.actual_run_time 

        # training logic
        # if time for retrain
        # or time for first train 
        if ((self.is_trained and len(self.train_batch) < RETRAIN_MAX) or 
            (not self.is_trained and len(self.train_batch) < TRAIN_MAX)):  
            self.train_batch = pd.concat([
                self.train_batch, 
                pd.DataFrame([job.input_params])], 
                ignore_index=True)
            # print(self.train_batch,pd.DataFrame([job.input_params]))
            return
        
        """
        fetching our regressor from our pickles
        """
        if self.pickling:
            self.regressor = self.depickle_regressor(self.train_iter)
            self.train_iter += 1
            self.is_trained = True
            self.train_batch = pd.DataFrame()
            return

        """
        Not pickling so we must train the model
        """

        # print(len(self.df))
        self.concat(self.train_batch)

        # temp code to verify dataframe
        X,y = self.transform_df(self.df,predictCol="timeTaken")

        # print("saved dataframe")
        # X.to_csv(f"results/{self.timestamp_id}/job-{self.job_type_str}-out.csv")
        regressor = self.get_regressor(X)

        startTime = time.process_time()

        self.regressor = regressor.fit(X, y)
        self.pickle_regressor(self.regressor, self.train_iter)

        endTime = time.process_time()
        print(self.job_type_str,'finsihed train on',self.df.shape[0],"data points - total time: ",endTime-startTime)

        # finishing the training
        self.is_trained = True
        self.train_batch = pd.DataFrame() # clear the batch 
        self.train_iter += 1 # inc train iter for pickling tracking and other stuff
            
    def predict(self,raw_job,quantile_idx):
        """
        pass in raw job given by the predict function in the simulator. 
        Then we will parse the job and put into a format for our predictor to understand 
        """
        if not self.regressor or not self.is_trained:
            print("WARNING WE HAVE NO REGRESSOR TO PREDICT ON, FORCING CRASH")
            exit()  

        x = pd.DataFrame([raw_job.input_params])

        if not self.is_within_bounds(x,self.get_column_bounds(self.df)):
            print("out of bounds...")
            return raw_job.user_estimated_run_time

        result = self.regressor.predict(x,quantiles=self.quantiles)
            
        return result[0][quantile_idx]

    def get_column_bounds(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Return the min and max of each column in the dataframe.
        """
        return pd.DataFrame({
            "min": df.min(),
            "max": df.max()
        })


    def is_within_bounds(self, df: pd.DataFrame, bounds: pd.DataFrame) -> bool:
        """
        Return True if every value in df is within the bounds.
        Return False immediately if anything is out of bounds.
        """
        for col in bounds.index:
            if not col in df: continue # skip if column is not in our bounds
            col_min = bounds.loc[col, "min"]
            col_max = bounds.loc[col, "max"]
            if not ((df[col] >= col_min) & (df[col] <= col_max)).all():
                return False
        return True

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
        import warnings

        self.drop_cols = defaultdict(list)
        if SHOULD_PICKLE:
            print("WARNING, we are pickling results, which is expensive")


        warnings.filterwarnings(
            "ignore",
            category=FutureWarning,
            message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.*"
        )

        self.drop_cols[job_types.JOB_TYPE_EXAMINIMDSNAP] = [ 
            "testNum",
            "units",
            "lattice",
            "lattice_constant",
            "lattice_offset_x",
            "lattice_offset_y",
            "lattice_offset_z",
            "lattice_ny",
            "lattice_nz",
            "ntypes",
            "type",
            "mass",
            "force_cutoff",
            "temperature_target",
            "temperature_seed",
            "neighbor_skin",
            "comm_exchange_rate",
            "thermo_rate",
            "comm_newton",
            "error"
        ]

        self.controllers = {}
        self.train_batch = pd.DataFrame()

        timestamp_id = time.time()
        for job_type in job_types.JOB_TYPE_RANGE:
            self.controllers[job_type] = Controller(
                job_type=job_type,
                timestamp_id=timestamp_id,
                quantiles=[0.1,0.5,0.99,1],
                input_file=options["input_file"],
                sliding_window=True,
                pickling=SHOULD_DEPICKLE,
                drop_cols=self.drop_cols[job_type])
            os.makedirs(f"results/{timestamp_id}/{job_types.JOB_TYPE_TO_STR[job_type]}")

        pass
    
    def predict(self, job, current_time, list_running_jobs):
        # when we start prediction follow this algorithm
        # P = quant.predict(), if P > requested_time: requested_time else P
        # maybe some methodogly could be used that if we our under a specfic runtime then we shouldn't predict
        controller = self.controllers[job.job_type]

        if not controller.is_trained:
            job.predicted_run_time = job.user_estimated_run_time
            return
        
        Q50 = 1
        Q99 = 2 
        Q100 = 3
        predict = controller.predict(job,quantile_idx=Q50) # [[q1,q2,q3]]

        if predict > job.user_estimated_run_time:
            job.predicted_run_time = job.user_estimated_run_time
        else:
            job.predicted_run_time = predict 
        # job.predicted_run_time = int(result[0][0]) # 50th

    """
    This function will be used to train and retrain the model

    For now we will just implement the intital train (5000 jobs) and worry about retraining later
    """
    def fit(self, job, current_time):
        controller = self.controllers[job.job_type]
        controller.fit(job) 