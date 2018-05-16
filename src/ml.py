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

def cross_validation_metrics(df, key_cols, target, folds):
    df = df.dropna(how = 'any')
    X = df[key_cols]
    y = np.array(df[target])
    overall_rmse = []
    overall_accuracy = []
    overall_median_error = []
    overall_mean_error = []
    overall_r2 = []
    corr = []
    kf = KFold(n_splits = folds)
    i = 1
    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y[train_index], y[test_index]
        rf = RandomForestRegressor(n_estimators = 500, bootstrap = True, max_depth = 50, max_features= 7, min_samples_leaf = 1)
        rf.fit(X_train, y_train)
        predictions = rf.predict(X_test)
        rmse = metrics.mean_squared_error(predictions, y_test)**(1/2)
        var = metrics.explained_variance_score(predictions,y_test)
        pearsoncorr = pearsonr(predictions, np.array(y_test))
        perror = abs(predictions - y_test)/y_test
        mperror = statistics.median(perror)
        error = abs(predictions - y_test)
        merror = error.mean()
        print("Fold " + str(i))
        print("RMSE: "+ str(rmse))
        print("Correlation: "+ str(pearsoncorr))
        print("Accuracy: " + str(1-mperror))
        print("Mean Error: "+ str(merror))
        print("Median Error: "+ str(statistics.median(error)))
        print("-------------------------")
        overall_rmse.append(rmse)
        overall_accuracy.append((1-mperror))
        overall_median_error.append(statistics.median(error))
        overall_mean_error.append(merror)
        #overall_r2.append(r2)
        corr.append(pearsoncorr[0])
        i = i+1

    return_dict = {
        'rmse': np.mean(overall_rmse),
        'accuracy': np.mean(overall_accuracy),
        'median_error': np.mean(overall_median_error),
        'mean_error' : np.mean(overall_mean_error),
        'correlation':np.mean(corr)
    }
    return return_dict

def buildModel(df, keyFeatures):
    categoryColumns = df.select_dtypes(include = ['category']).columns
    df["Name"] = pd.Categorical(df["Name"]).codes
    for col in categoryColumns:
        df[col] = pd.Categorical(df[col]).codes

    #print(df.info())
    rf = RandomForestRegressor(bootstrap = True, max_depth = 50, max_features = 7, min_samples_leaf = 1, n_estimators = 500)

    metrics = cross_validation_metrics(df, keyFeatures, "Wait", 10)

    rf.fit(df[keyFeatures], df["Wait"])

    return(rf)
