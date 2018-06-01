
def create_new_data(originalData):
    import statistics
    import matplotlib.pyplot as plt
    import pymysql
    import config
    import transformations
    import ml
    from sklearn.model_selection import KFold
    import pandas as pd
    from datetime import datetime
    from datetime import timedelta
    import numpy as np
    rides = originalData.Name.unique()

    today = datetime.now()
    currentDate = datetime.date(today)

    DayOfWeek = datetime.weekday(today)
    Weekend = 1 if DayOfWeek == 5 or DayOfWeek == 6 else 0
    newData = pd.DataFrame()
    conn = pymysql.connect(config.host, user = config.username, port = config.port, passwd = config.password)

    for ride in rides:
        rideData = originalData[originalData['Name'] == ride]
        rideStatic = {'Name': ride,
                      'Tier': rideData['Tier'].iloc[0],
                      'IntellectualProp': rideData['IntellectualProp'].iloc[0],
                      'ParkName': rideData['ParkName'].iloc[0],
                      'CharacterExperience': rideData['CharacterExperience'].iloc[0],
                      'DayOfWeek': DayOfWeek,
                      'Weekend': Weekend}
        rideFrame = pd.DataFrame(rideStatic, index = [0])
        getParkHours = "select * from DisneyDB.ParkHours phours join DisneyDB.Park park on phours.ParkId = park.Id where Name = '"+ rideStatic['ParkName'] + "' and Date = '" + str(currentDate)+"'"
        parkHours = pd.read_sql_query(getParkHours, conn)

        emhDay = 0 if parkHours.EMHOpen[0] == 'None' else 1
        rideFrame['EMHDay'] = emhDay
        parkHours['ParkOpen'] = pd.to_datetime(parkHours['ParkOpen'], format = '%I:%M %p').dt.strftime('%H:%M')
        parkHours['ParkOpen'] = pd.to_datetime(parkHours['ParkOpen'], format = '%H:%M').dt.time
        parkHours['ParkClose'] = pd.to_datetime(parkHours['ParkClose'], format = '%I:%M %p').dt.strftime('%H:%M')
        parkHours['ParkClose'] = pd.to_datetime(parkHours['ParkClose'], format = '%H:%M').dt.time
        parkHours["EMHOpen"] = pd.to_datetime(parkHours["EMHOpen"], format = '%I:%M %p', errors = 'coerce').dt.strftime('%H:%M')
        parkHours["EMHClose"] = pd.to_datetime(parkHours["EMHClose"], format = '%I:%M %p', errors = 'coerce').dt.strftime('%H:%M')
        parkHours["EMHOpen"] = pd.to_datetime(parkHours["EMHOpen"], format = '%H:%M', errors = 'coerce').dt.time
        parkHours["EMHClose"] = pd.to_datetime(parkHours["EMHClose"], format = '%H:%M', errors = 'coerce').dt.time

        parkOpen = parkHours.ParkOpen.iloc[0]
        parkClose = parkHours.ParkClose.iloc[0]
        emhOpen = parkHours.EMHOpen.iloc[0]
        emhClose = parkHours.EMHClose.iloc[0]

        if emhDay == 1:
            if emhClose == parkOpen:
                emhType = 'Morning'
            else:
                emhType = 'Night'

        pOpenToday = today.replace(hour = parkOpen.hour, minute = parkOpen.minute, second = 0, microsecond = 0)
        pCloseToday = today.replace(hour = parkClose.hour, minute= parkClose.minute, second = 0, microsecond = 0)
        if pCloseToday < pOpenToday:
            try:
                pCloseToday = pCloseToday.replace(day = pCloseToday.day + 1)
            except:
                try:
                    pCloseToday = pCloseToday.replace(month = pCloseToday.month + 1, day = 1)
                except:
                    pCloseToday = pCloseToday.replace(year = pCloseToday.year + 1, month = 1, day = 1)
        if emhDay == 1:
            eOpenToday = today.replace(hour = emhOpen.hour, minute = emhOpen.minute, second = 0, microsecond = 0)
            if eOpenToday.hour < 6:
                try:
                    eOpenToday = eOpenToday.replace(day = eOpenToday.day + 1)
                except:
                    try:
                        eOpenToday = eOpenToday.replace(month = eOpenToday.month + 1, day = 1)
                    except:
                        eOpenToday = eOpenToday.replace(year = eOpenToday.year + 1, month = 1, day = 1)
            eCloseToday = today.replace(hour = emhClose.hour, minute = emhClose.minute, second = 0, microsecond = 0)
            if (eCloseToday < pOpenToday) and (emhType == 'Night'):
                try:
                    eCloseToday = eCloseToday.replace(day = eCloseToday.day + 1)
                except:
                    try:
                        eCloseToday = eCloseToday.replace(month = eCloseToday.month + 1, day = 1)
                    except:
                        eCloseToday = eCloseToday.replace(year = eCloseToday.year + 1, month =1, day = 1)

        totalRideFrame = pd.DataFrame()
        startTime = eOpenToday if emhDay == 1 and emhType == 'Morning' else pOpenToday
        validTime = True
        currentTime = startTime
        midday = today.replace(hour = 14, minute = 0, second = 0, microsecond = 0)
        while validTime:

            timeSinceOpen = currentTime - startTime
            timeSinceMidDay = currentTime - midday
            if emhDay == 1:
                if (currentTime >= eOpenToday) and (currentTime <= eCloseToday):
                    inEMH = 1
                else:
                    inEMH = 0
            else:
                inEMH = 0

            minutesSinceOpen = int(round(timeSinceOpen.total_seconds()/60))
            timeSinceMidDayHours =  int(round(abs(timeSinceMidDay.total_seconds()/3600)))
            timeSinceOpenHours = int(round(timeSinceOpen.total_seconds()/3600))

            currentRow = rideFrame.copy()
            currentRow['TimeSinceOpen'] = timeSinceOpenHours
            currentRow['MinutesSinceOpen'] = minutesSinceOpen
            currentRow['TimeSinceMidday'] = timeSinceMidDayHours
            currentRow['inEMH'] = inEMH

            totalRideFrame = pd.concat([totalRideFrame,currentRow])

            newTime = currentTime + timedelta(minutes=15)
            if emhDay == 1:
                if emhType == 'Morning':
                    if (newTime >= eOpenToday) and (newTime <= pCloseToday):
                        validTime = True
                    else:
                        validTime = False
                else:
                    if (newTime <= pOpenToday) and (newTime <= eCloseToday):
                        validTime = True
                    else:
                        validTime = False
            else:
                if (newTime >= pOpenToday) and (newTime <= pCloseToday):
                    validTime = True
                else:
                    validTime = False
            currentTime = newTime
        newData = pd.concat([newData, totalRideFrame])
    #     print([startTime, endTime,emhDay, inEMH])
    conn.close()
