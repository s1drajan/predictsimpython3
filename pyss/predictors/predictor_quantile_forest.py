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

import pandas as pd
import time

import os

WINDOW_MAX = 6000 #10000
TRAIN_MAX = 5000
RETRAIN_MAX = 100 # https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7776517

"""
Each application gets there own Controller which wraps the necessary logic and functions
"""
class Controller():
    def __init__(self,job_type,timestamp_id,quantiles,sliding_window=False,drop_cols=[]): 
        self.model = RandomForestQuantileRegressor()
        self.df = pd.DataFrame()
        self.train_batch = pd.DataFrame()
        self.drop_cols = drop_cols

        self.job_type = job_type
        self.job_type_str = job_types.JOB_TYPE_TO_STR[job_type]
        self.is_trained = False
        self.quantiles = quantiles 
        self.is_sliding_window = sliding_window

        self.predicted_plot_x = []
        self.predicted_plot_y = [[] for _ in range(len(quantiles))]
        self.plot_iter = 0

        self.timestamp_id = timestamp_id

    def concat(self, new_df):
        # not sliding window or we aren't ready to trim the window
        if not self.is_sliding_window or self.df.shape[0] < WINDOW_MAX:
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            return
        
        # adjusting train window
        self.df = pd.concat([self.df.iloc[RETRAIN_MAX:],new_df],ignore_index=True)

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

        # drop cols
        for col in self.drop_cols:
            if not col in X.columns:
                # print(f"warning {col} not in dataset, not dropping")
                continue

            X = X.drop(columns=col)

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
    
    def get_pipeline(self, preprocessor, clf):
        """ 
        Convenience function to add a preprocessor to a regression pipeline.
        """
        return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", clf)])

    def get_regressor(self,X):
        preprocessor = self.generate_preprocessor(X)
        return self.get_pipeline(preprocessor, self.model)
    
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
        
        # plot logic
        # if self.is_trained:
            # self.plot()

        # print(len(self.df))
        self.concat(self.train_batch)

        # temp code to verify dataframe
        X,y = self.transform_df(predictCol="timeTaken")
        # X = X.to_numpy(dtype=np.float64)
        # from threadpoolctl import threadpool_info
        # print(threadpool_info())
        # print(X.shape,y.shape)

        # print("saved dataframe")
        # X.to_csv(f"results/{self.timestamp_id}/job-{self.job_type_str}-out.csv")
        regressor = self.get_regressor(X)
        # print(X.dtypes,regressor)
        print("got regressor")

        startTime = time.process_time()
        self.regressor = regressor.fit(X, y)
        endTime = time.process_time()
        print(self.job_type_str,'finsihed train on',self.df.shape[0],"data points - total time: ",endTime-startTime)

        # finishing the training
        self.is_trained = True
        self.train_batch = pd.DataFrame() # clear the batch 
            
    def predict(self,raw_job):
        """
        pass in raw job given by the predict function in the simulator. 
        Then we will parse the job and put into a format for our predictor to understand 
        """
        if not self.regressor or not self.is_trained:
            print("WARNING WE HAVE NO REGRESSOR TO PREDICT ON, FORCING CRASH")
            exit()  

        x = pd.DataFrame([raw_job.input_params])
        result = self.regressor.predict(x,quantiles=self.quantiles)
        r = result[0]
        for i in range(len(self.quantiles)):
            self.predicted_plot_y[i].append(r[i])
        self.predicted_plot_x.append(raw_job.actual_run_time)
            
        return result
    
    def plot(self):
        colors = ['blue','green','red']
        x = np.array(self.predicted_plot_x)
        for i in range(len(self.quantiles)):
            plt.scatter(
                x,
                np.array(self.predicted_plot_y[i]),
                c=colors[i],
                label=str(self.quantiles[i]),
                alpha=0.7)
        plt.scatter(x,x,c="black",label="actual_value",alpha=0.7)

        title = self.job_type_str+" train_iter: "+str(self.plot_iter)
        plt.xlabel("Actual Runtime")
        plt.ylabel("Predicted Runtime")
        plt.title(title)
        plt.legend()
        plt.savefig(f"results/{self.timestamp_id}/{self.job_type_str}/{title.replace(" ","-")}.png")
        plt.close()

        self.plot_iter+=1 

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
        self.drop_cols = defaultdict(list)
        import warnings
        import pandas as pd

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
                quantiles=[0.1,0.5,0.99],
                sliding_window=True,
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
        
        # print(controller.predict(job),job.actual_run_time)        
        result = controller.predict(job) # [[q1,q2,q3]]
        # print(result, type(result), type(result[0][0]))
        # print(result[0],job.actual_run_time)
        q50 = int(result[0][1])
        q99 = int(result[0][2])
        if q50 > job.user_estimated_run_time:
            job.predicted_run_time = job.user_estimated_run_time
        else:
            job.predicted_run_time = q50
        # job.predicted_run_time = int(result[0][0]) # 50th

    """
    This function will be used to train and retrain the model

    For now we will just implement the intital train (5000 jobs) and worry about retraining later
    """
    def fit(self, job, current_time):
        controller = self.controllers[job.job_type]
        controller.fit(job) 