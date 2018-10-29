# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from datetime import datetime
from pytz import timezone
from django_pandas.io import read_frame
import pandas as pd
from .generic_functions import fix_time

class Metrics(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Metrics'


class Park(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.
    openingdate = models.TextField(db_column='OpeningDate', blank=True, null=True)  # Field name made lowercase.
    displayname = models.TextField(db_column="DisplayName")
    latitude = models.FloatField(db_column = "Latitude")
    longitude = models.FloatField(db_column = "Longitude")
    imageurl = models.TextField(db_column = "ImageUrl")
    description = models.TextField(db_column = "Description")
    bannerurl = models.TextField(db_column = "BannerImageUrl")
    if (id == 10) or (id == 11):
        tz = timezone('US/Pacific')
    else:
        tz = timezone('US/Eastern')

    current_date = datetime.now(tz).date()

    def get_todays_parks_hours(self):
        park_hours_set = Parkhours.objects.filter(parkid = self.id).filter(date__gte = self.current_date)
        if len(park_hours_set) < 1:
            return None
        else:
            current_park_hours = park_hours_set[len(park_hours_set) - 1]
            return current_park_hours

    def current_weather(self):
        weather_set = self.weather_set.all()
        #ride_waits_set = RideWaits.objects.filter(rideid = self.id).filter(date__gte = datetime.date.today())
        if len(weather_set) < 1:
            return None
        else:
            weather_set = weather_set[len(weather_set) - 1]
            return weather_set

    class Meta:
        managed = False
        db_table = 'Park'


class Parkhours(models.Model):
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    parkid = models.ForeignKey(Park, db_column='ParkId', blank=True, null=True, on_delete = models.SET_NULL)  # Field name made lowercase.
    parkopen = models.TextField(db_column='ParkOpen', blank=True, null=True)  # Field name made lowercase.
    parkclose = models.TextField(db_column='ParkClose', blank=True, null=True)  # Field name made lowercase.
    emhopen = models.TextField(db_column='EMHOpen', blank=True, null=True)  # Field name made lowercase.
    emhclose = models.TextField(db_column='EMHClose', blank=True, null=True)  # Field name made lowercase.
    specialopen = models.TextField(db_column = "SpecialOpen", blank=True, null = True)
    specialclose = models.TextField(db_column = "SpecialClose", blank=True, null = True)

    class Meta:
        managed = False
        db_table = 'ParkHours'


class Ride(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    name = models.TextField(db_column='Name')  # Field name made lowercase.
    openingdate = models.TextField(db_column='OpeningDate', blank=True, null=True)  # Field name made lowercase.
    tier = models.TextField(db_column='Tier', blank=True, null=True)  # Field name made lowercase.
    location = models.TextField(db_column='Location')  # Field name made lowercase.
    parkid = models.ForeignKey(Park, db_column='ParkId', blank=True, null=True, on_delete = models.SET_NULL)  # Field name made lowercase.
    intellectualprop = models.CharField(db_column='IntellectualProp', max_length=45, blank=True, null=True)  # Field name made lowercase.
    haswaits = models.IntegerField(db_column = 'HasWaits')
    geolocation = models.TextField(db_column = 'GeoSearchName', null = True)
    description = models.TextField(db_column = 'Description', null = True)
    latitude = models.TextField(db_column = 'Latitude', null = True)
    longitude = models.TextField(db_column = 'Longitude', null = True)

    def current_status(self):
        current_status_set = self.ridecurrentstatus_set.all()
        if len(current_status_set) > 0:
            current_status = current_status_set[0]
            status = current_status.status
        else:
            return "No Status"
        return status

    def current_fastpass(self):
        current_status_set = self.ridecurrentstatus_set.all()
        if len(current_status_set)>0:
            current_fastpass = current_status_set[0]
            fastpass = current_fastpass.fastpass
        else:
            return "No Information Regarding Fastpass"
        return fastpass


    def current_time(self):
        ride_waits_set = self.todaywaits_set.all()
        #ride_waits_set = RideWaits.objects.filter(rideid = self.id).filter(date__gte = datetime.date.today())
        if len(ride_waits_set) < 1:
            return None
        else:
            current_ride_waits = ride_waits_set[len(ride_waits_set) - 1]
            return current_ride_waits.time

    def current_wait(self):
        ride_waits_set = self.todaywaits_set.all()
        #ride_waits_set = RideWaits.objects.filter(rideid = self.id).filter(date__gte = datetime.date.today())
        if len(ride_waits_set) < 1:
            return None
        else:
            current_ride_waits = ride_waits_set[len(ride_waits_set) - 1]
            return current_ride_waits.wait

    def todays_waits(self):
        ride_waits_set = self.todaywaits_set.all().order_by('time')
        if len(ride_waits_set) < 1:
            return None
        else:
            return ride_waits_set

    def return_location_string(self):
        if (self.latitude) and (self.longitude):
            return (str(self.latitude)+","+str(self.longitude))

        elif self.geolocation:
            return self.geolocation

        else:
            current_park = Park.objects.filter(id = self.parkid)
            if self.location:
                return str(self.location) + str(current_park.name)
            else:
                return current_park.name

    def predicted_waits(self):
        predicted_set = self.todaywaitspredicted_set.all()
        return predicted_set

    def get_best_times_to_go(self):
        latest_time = self.current_time()
        tempTime = datetime.now()
        tempTime = tempTime.replace(minute = int(latest_time.split(":")[1]), hour = int(latest_time.split(":")[0]), second = 0, microsecond = 0)
        predicted_set = self.predicted_waits()
        today_predictions = read_frame(predicted_set)
        today_predictions['time'] = pd.to_datetime(today_predictions['time'], infer_datetime_format = True)
        remaining_predictions = today_predictions[today_predictions['time'] > tempTime]
        shortest_wait = min(remaining_predictions['predictedwait'])
        time_to_come_back = remaining_predictions[remaining_predictions['predictedwait'] == shortest_wait]['time']
        time_to_come_back = time_to_come_back.iloc[0]
        time_to_come_back = time_to_come_back.strftime("%I:%M %p")
        time_to_come_back = fix_time(time_to_come_back)

        return_times = {}

        if remaining_predictions.shape[0] > 4:
            next_hour = remaining_predictions.iloc[0:4]
            shortest_in_next_hour = min(next_hour['predictedwait'])
            time_next_hour = next_hour[next_hour['predictedwait'] == shortest_in_next_hour]['time']
            time_next_hour = time_next_hour.iloc[0]
            time_next_hour = time_next_hour.strftime("%I:%M %p")
            time_next_hour = fix_time(time_next_hour)
        else:
            time_next_hour = None


        return_times['nexthour'] = time_next_hour
        return_times['nexthourwait'] = shortest_in_next_hour
        return_times['remainingday'] = time_to_come_back
        return_times['remainingdaylow'] = shortest_wait
        return return_times

    class Meta:
        managed = False
        db_table = 'Ride'


class RideWaits(models.Model):
    rideid = models.ForeignKey(Ride,db_column='RideId', on_delete = models.SET_NULL, null = True)  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TextField(db_column='Time')  # Field name made lowercase.
    wait = models.IntegerField(db_column='Wait')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Ride_Waits'

class TodayWaits(models.Model):
    rideid = models.ForeignKey(Ride,db_column='RideId', on_delete = models.SET_NULL, null = True)  # Field name made lowercase.
    date = models.DateField(db_column='Date')  # Field name made lowercase.
    time = models.TextField(db_column='Time')  # Field name made lowercase.
    wait = models.IntegerField(db_column='Wait')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Ride_Waits_Today'

class Weather(models.Model):
    date = models.CharField(db_column='Date', max_length=45)  # Field name made lowercase.
    time = models.TextField(db_column='Time')  # Field name made lowercase.
    status = models.TextField(db_column='Status')  # Field name made lowercase.
    temperature = models.FloatField(db_column='Temperature')  # Field name made lowercase.
    cloudcover = models.FloatField(db_column='CloudCover')  # Field name made lowercase.
    simplestatus = models.TextField(db_column='SimpleStatus')  # Field name made lowercase.
    rainaccumulation = models.FloatField(db_column='RainAccumulation')  # Field name made lowercase.
    iconname = models.TextField(db_column = 'IconName')
    parkid = models.ForeignKey(Park, db_column='ParkId', blank=True, null=True, on_delete = models.SET_NULL)  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'Weather'


class RideCurrentStatus(models.Model):
    rideid = models.ForeignKey(Ride, db_column = 'RideId', on_delete = models.DO_NOTHING, primary_key = True)
    status = models.TextField(db_column = 'Status')
    fastpass = models.TextField(db_column = 'FastPassAvailable')

    class Meta:
        managed = False
        db_table = 'Ride_Current_Status'

class TodayWaitsPredicted(models.Model):
    rideid = models.ForeignKey(Ride, db_column = 'RideId', on_delete = models.SET_NULL, null = True)
    time = models.TextField(db_column = 'Time')
    predictedwait = models.IntegerField(db_column = 'PredictedWait')
    confidencelow = models.IntegerField(db_column = 'ConfidenceLow')
    confidencehigh = models.IntegerField(db_column = 'ConfidenceHigh')

    class Meta:
        managed = False
        db_table = 'Ride_Waits_Today_Predicted'


class UserRideFavorite(models.Model):
    userid = models.IntegerField(db_column = "UserId")
    rideid = models.IntegerField(db_column = 'RideId')

    class Meta:
        db_table = 'User_Ride_Favorites'
