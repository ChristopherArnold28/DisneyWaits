import pymysql
import pandas as pd
import numpy as np
from datetime import datetime
import config

conn = pymysql.connect(config.host, user=config.username,port=config.port,
                           passwd=config.password)

query = "call DisneyDB.RideWaitQuery"

RideWaits = pd.read_sql_query(query, conn)

print(RideWaits.head())
