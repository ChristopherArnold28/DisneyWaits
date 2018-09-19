import requests
import json
import sys
from datetime import datetime, timedelta
from disney_auth import get_header


class Park(object):
    def __init__(self, id = ''):
        # This function works by querying the disney api to grab all information
        # related to this specific park as given by the id
        # the id' can be found in the parkIds.txt file
        try:
            if id == '':
                raise ValueError('Park object expects an ID. Must be passed as string as follows:\n Park(id)')
            elif id != None and type(id) != str:
                raise TypeError('Park object expects a string input for the ID')

            self.__park_id = id
            try:
                authentication = get_header()
                s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/theme-parks/{}".format(self.__park_id), headers=authentication)
                self.__park_data = json.loads(s.content)

                if self.__park_data['errors'] != []:
                    s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/water-parks/{}".format(self.__park_id), headers=authentication)
                    self.__park_data = json.loads(s.content)

            except:
                pass

            self.__park_name = self.__park_data['name']
        except ValueError as e:
            print(e)
            sys.exit()
        except TypeError as e:
            print(e)
            sys.exit()
        except Exception as e:
            print(e)
            sys.exit()

    def getParkId(self):
        return self.__park_id

    def getParkName(self):
        return self.__park_name


    def getTodayParkHours(self, date = 'Today'):
        if date == 'Today':
            DATE = datetime.today()

        else:
            DATE = date

        authentication = get_header()
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/schedules/{}?date={}-{}-{}".format(self.__park_id, DATE.year, self.__formatDate(str(DATE.month)), self.__formatDate(str(DATE.day))), headers=authentication)

        schedule_data = json.loads(s.content)

        park_open = None
        park_close = None
        emh_open = None
        emh_close = None
        special_open = None
        special_close = None

        schedules = schedule_data['schedules']

        try:

            for item in schedules:
                if item['type'] == 'Operating':
                    park_open = datetime(DATE.year, DATE.month, DATE.day, int(item['startTime'][0:2]), int(item['startTime'][3:5]))
                    if int(item['endTime'][0:2]) >= 0 and int(item['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days = 1)
                        park_close = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(item['endTime'][0:2]), int(item['endTime'][3:5]))
                    else:
                        park_close = datetime(DATE.year, DATE.month, DATE.day, int(item['endTime'][0:2]), int(item['endTime'][3:5]))

                if item['type'] == 'Extra Magic Hours':
                    emh_open = datetime(DATE.year, DATE.month, DATE.day, int(item['startTime'][0:2]), int(item['startTime'][3:5]))
                    if int(item['endTime'][0:2]) >= 0 and int(item['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days = 1)
                        emh_close = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(item['endTime'][0:2]), int(item['endTime'][3:5]))
                    else:
                        emh_close = datetime(DATE.year, DATE.month, DATE.day, int(item['endTime'][0:2]), int(item['endTime'][3:5]))

                if item['type'] == 'Special Ticketed Event':
                    special_open = datetime(DATE.year, DATE.month, DATE.day, int(item['startTime'][0:2]), int(item['startTime'][3:5]))
                    if int(item['endTime'][0:2]) >= 0 and int(item['endTime'][0:2]) <= 7:
                        DATETEMP = DATE + timedelta(days = 1)
                        special_close = datetime(DATETEMP.year, DATETEMP.month, DATETEMP.day, int(item['endTime'][0:2]), int(item['endTime'][3:5]))
                    else:
                        special_close = datetime(DATE.year, DATE.month, DATE.day, int(item['endTime'][0:2]), int(item['endTime'][3:5]))

        except KeyError:
            pass

        return {
            'park_open': park_open,
            'park_close': park_close,
            'emh_open' : emh_open,
            'emh_close':emh_close,
            'special_open':special_open,
            'special_close':special_close
        }


    def getCurrentWaitTimes(self):
        authentication = get_header()
        s = requests.get("https://api.wdpro.disney.go.com/facility-service/theme-parks/{}/wait-times".format(self.__park_id), headers=authentication)
        wait_data = json.loads(s.content)

        wait_entries = wait_data['entries']
        ride_wait_data = {}
        for item in wait_entries:
            #print(item['id'].split(';')[0] + " " +item['name'])
            current_dict = {}
            current_dict["ride_id"] = item['id'].split(';')[0]
            current_dict["ride_name"] = item['name']
            wait_info = item['waitTime']
            if 'postedWaitMinutes'in wait_info:
                current_dict['wait_time'] = wait_info['postedWaitMinutes']
            if 'fastPass' in wait_info:
                current_dict['fast_pass_info'] = wait_info['fastPass']

            ride_wait_data[current_dict["ride_id"]] = current_dict

        return ride_wait_data

    def getOpenAttractionIds(self):
        wait_data = self.getCurrentWaitTimes()
        attractions = list(wait_data.keys())

        return attractions

    def __formatDate(self, num):
        # make all months and dates into two digit months and dates
        if len(num) < 2:
            num = '0' + num
        return num
