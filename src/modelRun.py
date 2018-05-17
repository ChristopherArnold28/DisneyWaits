#import packages
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
import ml
from sklearn.model_selection import KFold

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)

#gather all historical data to build model
RideWaits = pd.read_sql_query("call DisneyDB.RideWaitQuery", conn)

#transform data for model bulding
RideWaits = transformations.transformData(RideWaits)

#build model based on historical data and save some important metrics
keyFeatures = ["Name","MagicHourType", "Tier", "IntellectualProp", "SimpleStatus", "ParkName", "DayOfWeek", "Weekend", "TimeSinceOpen", "CharacterExperience", "TimeSinceMidday", "inEMH", "EMHDay"]
newModel = ml.buildModel(RideWaits, keyFeatures, "Wait")

#gather new data based on all rides and build time frame based on open/close
#and weather forecasts


#predict data


#save daily predictions to the database
