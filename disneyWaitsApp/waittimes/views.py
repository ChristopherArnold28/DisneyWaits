from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from .models import Park, Ride, Parkhours, RideWaits, Weather, UserRideFavorite, UserNotifications, UserPhonenumber
import json
from .generic_functions import fix_time
from datetime import datetime
from django.contrib.auth.decorators import login_required
import pymysql
import pandas as pd
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import NotificationForm
from .forms import PhonenumberForm
import requests
import config
# Create your views here.

def terms_of_use(request):
    return render(request, 'terms_of_use.html')

def parks_list(request):
    park_list = Park.objects.all()
    context = {'park_list': park_list}
    return render(request, 'parks_list.html', context)

def park_detail(request, park_id):
    park = get_object_or_404(Park,pk = park_id)
    ride_list = park.ride_set.filter(haswaits = 1)

    valid_rides = [x  for x in ride_list if x.current_wait() is not None]
    valid_rides = [x for x in valid_rides if x.current_status() == "Operating"]

    sorted_waits = sorted(valid_rides, key = lambda x: x.current_wait(), reverse = True)

    top_waits = sorted_waits[:5]
    lowest_waits = sorted_waits[-5:]
    weather = park.current_weather()
    weather_url = "http://openweathermap.org/img/w/"+ str(weather.iconname) +".png"

    context = {'park':park,
               'rides_with_waits':ride_list,
               'top_waits':top_waits,
               'lowest_waits':lowest_waits[::-1],
               'current_weather':weather,
               'weather_url':weather_url}
    return render(request, 'park_detail.html', context)

def ride_detail(request, ride_id):
    user = None
    doesnt_follow = True
    if request.user.is_authenticated:
        user = request.user
        if len(UserRideFavorite.objects.filter(userid = int(request.user.id), rideid = int(ride_id))) > 0:
            doesnt_follow = False

    ride = get_object_or_404(Ride, pk = ride_id)

    wait_times = ride.todaywaits_set.all()

    categories = list()
    observed_waits_data = list()

    categories_predicted = list()
    predicted_wait_times_list = list()

    predicted_wait_times = ride.predicted_waits()

    predicted_series_data = []
    observed_series_data = []
    confidence_interval_series = []

    today = datetime.today()
    ep = datetime(1970,1,1,0,0,0)
    for obs in predicted_wait_times:
        hours = int(str(obs.time)[0:2])
        minutes = int(str(obs.time)[3:5])

        today = today.replace(hour = hours, minute = minutes, second = 0, microsecond = 0)
        time = (today - ep).total_seconds()*1000

        current_tup = [time, obs.confidencelow, obs.confidencehigh]
        confidence_interval_series.append(current_tup)



    for obs in predicted_wait_times:
        hours = int(str(obs.time)[0:2])
        minutes = int(str(obs.time)[3:5])

        today = today.replace(hour = hours, minute = minutes, second = 0, microsecond = 0)
        time = (today - ep).total_seconds()*1000

        current_tup = [time, obs.predictedwait]
        predicted_series_data.append(current_tup)

        categories_predicted.append(fix_time(obs.time))
        predicted_wait_times_list.append(obs.predictedwait)

    for obs in wait_times:
        hours = int(str(obs.time)[0:2])
        minutes = int(str(obs.time)[3:5])

        today = today.replace(hour = hours, minute = minutes, second = 0, microsecond = 0)
        time = (today - ep).total_seconds()*1000
        current_tup = [time, obs.wait]
        categories.append(fix_time(obs.time))
        observed_waits_data.append(obs.wait)
        current_dict = {'name':fix_time(obs.time),
        'y': obs.wait}

        observed_series_data.append(current_tup)




    observed_waits = {
        'name': "Observed Wait Time",
        'data': observed_series_data,
        'marker':{'enabled': False},
        'zIndex':2,
        'type':'spline'
    }

    predicted_waits = {
        'name': "Anticipated Wait Time",
        'data': predicted_series_data,
        'marker':{'enabled':False,
                'lineColor': 'Highcharts.getOptions().colors[0]'},
        'zIndex':1,
        'type':'spline'
    }

    confidence_window = {
        'name': 'Anticipated Range',
        'type':'arearange',
        'data': confidence_interval_series,
        'lineWidth': 0,
        'color': 'rgba(84,190,231,1)',
        'linkedTo': ':previous',
        'fillOpacity': 0.15,
        'zIndex': 0,
        'marker': {
            'enabled': False
        }
    }


    tickInterval = 2

    if len(categories) > 10:
        tickInterval = 5

    if len(categories) > 25:
        tickInterval = 8

    if len(categories) > 35:
        tickInterval = 10



    series = [observed_waits]
    chart_title = "Wait Times for " + str(ride.name)
    chart = {
        'title': {'text': chart_title},
        'xAxis': {'type': 'datetime',
                  'dateTimeLabelFormats': {
                    'day': '%e of %b',
                    'minute':  '%I:%M',
                    'hour': '%I:%M'
                    }},
        'yAxis':{'title':{
            'text': "Wait(Minutes)"
        }},
        'tooltip':{
            'xDateFormat': '%I:%M',
            'crosshairs':True,
            'shared':True
        },
        'series': [ predicted_waits, observed_waits,confidence_window]
    }

    dump = json.dumps(chart)


    context = {
        'ride':ride,
        'chart':dump,
        'current_user':user,
        'doesnt_follow': doesnt_follow
    }
    return render(request, 'ride_detail.html', context)


def no_wait_rides(request, park_id):
    park = get_object_or_404(Park, pk = park_id)
    attraction_list = park.ride_set.filter(haswaits = 0)
    context = {'park':park,
               'other_attractions':attraction_list}

    return render(request, 'other_attractions.html', context)


def all_wait_times(request, park_id):
    park = get_object_or_404(Park, pk = park_id)
    attraction_list = park.ride_set.filter(haswaits = 1)
    context = {'park':park,
               'rides_with_waits':attraction_list}

    return render(request, 'park_wait_times.html', context)


@login_required
def user_home_page(request):
    username = request.user.username
    full_name = str(request.user.first_name) +" "+ str(request.user.last_name)
    userid = request.user.id
    ride_objects = None
    followed_rides = UserRideFavorite.objects.filter(userid = int(request.user.id))
    phone_numbers = UserPhonenumber.objects.filter(userid = int(request.user.id))
    numbers = None
    if len(phone_numbers) > 0:
        numbers = phone_numbers
    if len(followed_rides) > 0:
        ride_ids = [x.rideid for x  in followed_rides]
        ride_objects = Ride.objects.filter(id__in = ride_ids)

    context = {'current_user_name':username,
                'current_user_id':userid,
                'rides': ride_objects,
                'full_name': full_name,
                'phone_number': numbers}
    return render(request, 'user_home_page.html', context)




@login_required
def update_favorite(request, ride_id):
    doesnt_follow = True

    if request.user.is_authenticated:
        user = request.user
        if len(UserRideFavorite.objects.filter(userid = int(request.user.id), rideid = int(ride_id))) > 0:
            doesnt_follow = False

    if doesnt_follow:
        current_user_id = request.user.id
        ride_id = int(ride_id)

        favorite = UserRideFavorite()
        favorite.userid = current_user_id
        favorite.rideid = ride_id

        favorite.save()

    else:
        current_user_id = request.user.id
        ride_id = int(ride_id)
        UserRideFavorite.objects.filter(userid = int(request.user.id), rideid = int(ride_id)).delete()

    return HttpResponseRedirect(reverse('ride_detail', args = (ride_id,)))


@login_required
def add_notifications(request, ride_id):
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            new_notification = UserNotifications()
            new_notification.userid = request.user.id
            new_notification.rideid = ride_id
            user_number = UserPhonenumber.objects.filter(userid = request.user.id)
            if len(user_number) > 0:
                this_user = user_number[0]
                new_notification.phonenumber = this_user.phonenumber
            new_notification.datestart = form.cleaned_data['datestart']
            new_notification.dateend = form.cleaned_data['dateend']

            new_notification.save()
            return redirect('user_home_page')
    else:
        form = NotificationForm()
    return render(request, 'notification_setup.html', {'form':form})

@login_required
def add_phonenumber(request):
    if request.method == "POST":
        form = PhonenumberForm(request.POST)
        if form.is_valid():
            new_number = UserPhonenumber()
            new_number.userid = request.user.id
            new_number.phonenumber = form.cleaned_data['phonenumber']

            new_number.save()
            return redirect('user_home_page')
    else:
        form = PhonenumberForm()
    return render(request, 'add_number.html', {'form':form})

@login_required
def remove_notification(request, ride_id):
    current_user_id = request.user.id
    ride_id = int(ride_id)
    UserNotifications.objects.filter(userid = int(request.user.id), rideid = int(ride_id)).delete()

    return redirect('user_home_page')

@login_required
def go_to_ride(request, ride_id, lat_long):
    current_user_id = request.user.id

    test = True
    if test:
        lat_long = "28.418432,-81.5802548"

    latitude = lat_long.split(",")[0]
    longitude = lat_long.split(",")[1]

    ride = get_object_or_404(Ride, pk = ride_id)

    ride_lat = str(ride.latitude)
    ride_long = str(ride.longitude)

    origin = "origin="+latitude+","+longitude
    destination = "destination="+ride_lat+","+ride_long
    apikey = config.google_maps_api_key
    full_string = "https://www.google.com/maps/embed/v1/directions?key="+str(apikey) +"&"+ origin +"&" + destination + "&mode=walking"
    # answer = requests.get(full_string)
    # json_object = answer.json()
    # polyline = json_object['routes'][0]['overview_polyline']['points']
    # ride_id = int(ride_id)
    context = {
        'ride_id':ride_id,
        'lat_long':lat_long,
        'return':full_string
    }
    return render(request, 'go_to_ride.html',context)
