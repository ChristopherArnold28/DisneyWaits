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