from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_predict
import sklearn.metrics as metrics
from scipy.stats.stats import pearsonr
import pandas as pd
import numpy as np
from datetime import datetime
import statistics
import matplotlib.pyplot as plt
import pymysql
import config
import transformations

def saveMetrics(df, connection):


def buildModel(df, keyFeatures):
    categoryColumns = df.select_dtypes(include = ['category']).columns
    df["Name"] = pd.Categorical(df["Name"]).codes
    for col in categoryColumns:
        df[col] = pd.Categorical(df[col]).codes

    #print(df.info())
    rf = RandomForestRegressor(bootstrap = True, max_depth = 50, max_features = 7, min_samples_leaf = 1, n_estimators = 500)
    predictions = cross_val_predict(rf, df[keyFeatures], df["Wait"], cv = 5)

    rmse = metrics.mean_squared_error(predictions, df["Wait"])**(1/2)
    r2 = metrics.r2_score(predictions, df["Wait"])
    var = metrics.explained_variance_score(predictions,df["Wait"])
    pearsoncorr = pearsonr(predictions, df["Wait"])
    perror = abs(predictions - df["Wait"])/df["Wait"]
    mperror = statistics.median(perror)
    error = abs(predictions - df["Wait"])
    merror = error.mean()

    rf.fit(df[keyFeatures], df["Wait"])

    return(rf)



# print(rmse)
# print(r2)
# print(var)
# print(pearsoncorr)
# print(mperror)
# print(statistics.median(error))
# print(merror)
#
# fig, ax = plt.subplots(figsize = (20,20))
# plt.scatter(df["Wait"], predictions)
# plt.show()
#
# fig,ax = plt.subplots(figsize = (15,15))
# plt.scatter(df["Wait"], error)
# plt.show()
