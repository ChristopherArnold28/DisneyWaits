from django import template
from ..models import Park
from ..models import Ride
from ..models import TodayWaitsPredicted
register = template.Library()

@register.simple_tag
def list_of_parks():
    return {'parks_list': Park.objects.all()}

@register.simple_tag
def recommend_ride(ride):
    if ride.current_status() == "Operating":
        time_stamp = ride.current_time()
        match_string = str(time_stamp)+":00"
        waits_set = ride.todaywaitspredicted_set.filter(time = match_string)
        if ride.current_wait() is not None:
            #tell if a ride is recommended or not by how the current wait compares to the confidence interval
            if len(waits_set) <1:
                return "normal"
            else:
                current_anticipated = waits_set[len(waits_set) - 1]
                confidence_low = current_anticipated.confidencelow
                confidence_high = current_anticipated.confidencehigh
                window_high = confidence_high + 5
                window_low = confidence_low - 5

                current_wait = ride.current_wait()
                if current_wait > window_high:
                    return "avoid"
                elif current_wait > confidence_high:
                    return "normalhigh"
                elif current_wait > confidence_low:
                    return "normal"
                elif current_wait > window_low:
                    return "normallow"
                else:
                    return "recommended"
    else:
        return None



@register.simple_tag
def return_anticipated_wait(ride, time_stamp):
    match_string = str(time_stamp)+":00"
    waits_set = ride.todaywaitspredicted_set.filter(time = match_string)
    if len(waits_set) <1:
        return None
    else:
        current_anticipated = waits_set[len(waits_set) - 1]
        return current_anticipated.predictedwait

@register.simple_tag
def return_map_url(search_string, display_name, is_ride = 0):
    search_string = search_string.replace(" ","+")
    if is_ride == 1:
        url = "https://maps.googleapis.com/maps/api/staticmap?center="+str(search_string) + "&zoom=16&size=400x400&markers=color:green|" + str(search_string)+"&maptype=hybrid&key=AIzaSyBbzzZQCWEhTXjac4FKpqU5xKby2pKXL9M"
    else:
        url = "https://maps.googleapis.com/maps/api/staticmap?center="+str(search_string) + "&zoom=15&size=400x400&&markers=color:red|" + str(search_string)+"&maptype=hybrid&key=AIzaSyBbzzZQCWEhTXjac4FKpqU5xKby2pKXL9M"
    return {'url':url}

@register.simple_tag
def fix_time(time_string):
    if ("AM" in time_string) or ("PM" in time_string):
        time_string = time_string[1:] if time_string.startswith('0') else time_string
        return time_string

    first_half = time_string.split(":")[0]
    second_half = time_string.split(":")[1]
    if int(first_half) ==0:
        first_half = "12"
        time_string = str(first_half) + ":" + second_half + " AM"
    elif int(first_half)>12:
        first_half = int(first_half) - 12
        time_string = str(first_half) + ":" + second_half + " PM"
    elif int(first_half) == 12:
        time_string = first_half + ":" + second_half + " PM"
    else:
        time_string = str(int(first_half)) + ":" + second_half + " AM"

    return time_string
