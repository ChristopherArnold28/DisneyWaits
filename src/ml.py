from sklearn.ensemble import RandomForestRegressor
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
from sklearn.model_selection import KFold

def saveMetrics(df, connection):
    conn = pymysql.connect(config.host, user=config.username,port=config.port,
                               passwd=config.password)
    cur = conn.cursor()
    for index, row in df.iterrows():
        insertStatment = "insert into DisneyDB.Metrics (Name, Value) values ('"+ str(row["Metric Name"]) + "'," + str(row["Metric Value"])+")"
        cur.execute(insertStatment)
        conn.commit()

def cross_validation_metrics(df, target, folds):
    df = df.dropna(how = 'any')
    X = df.drop([target], axis = 1)
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
        rf = RandomForestRegressor(n_estimators = 1800,max_features = 8, min_samples_split = 4, min_samples_leaf = 1,max_depth = 60)
        rf.fit(X_train, y_train)
        predictions = rf.predict(X_test)
        predictions = predictions[y_test>0]
        y_test = y_test[y_test>0]
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


def buildModel(df, keyFeatures, target):
    fittingFrame = df[[keyFeatures,target]]
    fittingFrame["Name"] = pd.Categorical(fittingFrame["Name"])
    categoryColumns = df.select_dtypes(include = ['category']).columns
    for col in categoryColumns:
        currentCategorical = pd.get_dummies(fittingFrame[col])
        fittingFrame = pd.concat([fittingFrame,currentCategorical], axis = 1)

    #print(df.info())
    rf = RandomForestRegressor(n_estimators = 1800,max_features = 8, min_samples_split = 4, min_samples_leaf = 1,max_depth = 60)

    metrics = cross_validation_metrics(fittingFrame, target, 10)
    metric_frame = pd.DataFrame(list(metrics.items()), columns = ['Metric Name', 'Metric Value'])
    X = fittingFrame.drop([target], axis = 1)
    connection = {
        'host' : config.host,
        'dbname' : config.dbname,
        'username' : config.username,
        'password' : config.password,
        'port' : config.port
    }

    saveMetrics(metric_frame,connection)

    rf.fit(X, fittingFrame[target])
    # returns = {
    #     'model':rf,
    #     'metrics':metrics
    # }
    return(rf)
