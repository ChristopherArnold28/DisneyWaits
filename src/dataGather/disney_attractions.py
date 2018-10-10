import requests
import json
import sys
from datetime import datetime, timedelta
from disney_auth import get_header
from disney_parks import Park
import re

class Attraction(object):

    def __init__(self,id = ''):
        try:
            if id == '':
                    raise ValueError('Attraction object expects an id value. Must be passed as string.\n Usage: Attraction(id)')
            elif id != None and type(id) != str:
                raise TypeError('Attraction object expects a string argument.')

            self.__attraction_id = id

            authentication = get_header()
            s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/attractions/{}".format(self.__attraction_id), headers=authentication)
            self.__data = json.loads(s.content)

            self.__attraction_name = self.__data['name'].replace(u"\u2019", "").replace(u"\u2013", " ").replace(u"\u2122", "").replace(u"\u2022", " ")
            self.__attraction_name = self.__attraction_name.replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").replace(u"\u25cf", " ")
            self.__attraction_name = self.__attraction_name.replace(u"\u00e9", "e").replace(u"\u00ad", "").replace(u"\u00a0", " ").replace(u"\u00e8", "e").replace(u"\u00eb", "e").replace(u"\u2026", "...").replace(u"\u00e4", "a")
            self.__attraction_name = self.__attraction_name.replace(u"\u2018", "").replace(u"\u00ed", "i").replace(u"\u201c", '').replace(u"\u201d", '').replace("'","").replace(u"\u2013",' ').strip()
            try:
                self.__coordinates = (self.__data["coordinates"]["Guest Entrance"]["gps"]["latitude"], self.__data["coordinates"]["Guest Entrance"]["gps"]["longitude"])
            except:
                self.__coordinates = ()

        except ValueError as e:
            print(e)
            sys.exit()
        except TypeError as e:
            print(e)
            sys.exit()
        except Exception as e:
            print(e)
            print('That attraction or ID is not available. ID = {}\n Full list of possible attractions and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/attractions.txt'.format(id))
            sys.exit()


    def getAttractionData(self):
        return self.__data

    def getAttractionName(self):
        return self.__attraction_name

    def getAttractionID(self):
        return self.__attraction_id

    def getAttractionCoordinates(self):
        return self.__coordinates

    def getAncestorLand(self):
        try:
            return self.__data['links']['ancestorLand']['title'].replace("-"," ").replace(u"\u2013", " ").replace("'","")
        except:
            return None

    def getMobileDescription(self):
        try:
            string = self.__data['descriptions']['shortDescriptionMobile']['text'].replace(u"\u201c"," ").replace(u"\u201d"," ").replace(u"\u2019"," ").replace(u"\u2014", " ").replace(u"\u2022", " ").replace(u"\u2026", " ").replace(u"\u2013", " ")
            string = string.replace(u"\u2018", " ").replace(u"\u2122", " ")
            string = string.replace('"', "'")
            string = re.sub("<.?a.*?>","",string)
            return string
        except:
            return "No available description"
