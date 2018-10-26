from django.urls import path
from django.urls import re_path
from django.conf.urls import url
from . import views

urlpatterns = [
    #ex:/
    path('', views.parks_list, name = 'parks_list'),
    url(r'^park/(?P<park_id>[0-9]+)/$', views.park_detail, name = 'park_detail'),
    url(r'^park/(?P<park_id>[0-9]+)/all_other_attractions/$',views.no_wait_rides, name = 'other_attraction_list'),
    url(r'^park/(?P<park_id>[0-9]+)/all_wait_times/$',views.all_wait_times, name = 'all_attractions_with_waits'),
    url(r'^ride/(?P<ride_id>[0-9]+)/$', views.ride_detail, name = 'ride_detail'),
]
