import requests
import json
import sys
from datetime import datetime, timedelta
from disney_auth import get_header
from disney_parks import Park
from disney_points_of_interest import PointOfInterest
import re

class Entertainment(object):

    def __init__(self,id = ''):
        try:
            if id == '':
                    raise ValueError('Entertainment object expects an id value. Must be passed as string.\n Usage: Attraction(id)')
            elif id != None and type(id) != str:
                raise TypeError('Entertainment object expects a string argument.')

            self.__entertainment_id = id

            authentication = get_header()
            s = requests.get("https://api.wdpro.disney.go.com/global-pool-override-B/facility-service/entertainments/{}".format(self.__entertainment_id), headers=authentication)
            self.__data = json.loads(s.content)

            self.__entertainment_name = self.__data['name'].replace(u"\u2019", "").replace(u"\u2013", " ").replace(u"\u2122", "").replace(u"\u2022", " ")
            self.__entertainment_name = self.__entertainment_name.replace(u"\u00ae", "").replace(u"\u2014", "-").replace(u"\u00a1", "").replace(u"\u00ee", "i").replace(u"\u25cf", " ")
            self.__entertainment_name = self.__entertainment_name.replace(u"\u00e9", "e").replace(u"\u00ad", "").replace(u"\u00a0", " ").replace(u"\u00e8", "e").replace(u"\u00eb", "e").replace(u"\u2026", "...").replace(u"\u00e4", "a")
            self.__entertainment_name = self.__entertainment_name.replace(u"\u2018", "").replace(u"\u00ed", "i").replace(u"\u201c", '').replace(u"\u201d", '').replace("'","").replace(u"\u2013",' ').strip()
            try:
                self.__coordinates = self.getRelatedLocations()[0].getPointOfInterestCoordinates()
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
            print('That entertainment or ID is not available. ID = {}\n Full list of possible entertainment and their ID\'s can be found here: https://scaratozzolo.github.io/MouseTools/entertainments.txt'.format(id))
            sys.exit()

    def getMobileDescription(self):
        try:
            string = self.__data['descriptions']['shortDescriptionMobile']['text'].replace(u"\u201c"," ").replace(u"\u201d"," ").replace(u"\u2019"," ").replace(u"\u2014", " ").replace(u"\u2022", " ").replace(u"\u2026", " ").replace(u"\u2013", " ")
            string = string.replace(u"\u2018", " ").replace(u"\u2122", " ").replace(u"\u2015", " ")
            string = string.replace('"', "'")
            string = re.sub("<.?a.*?>","",string)
            return string
        except:
            return "No available description"

    def getEntertainmentData(self):
        return self.__data

    def getEntertainmentName(self):
        return self.__entertainment_name

    def getEntertainmentID(self):
        return self.__entertainment_id

    def getAttractionCoordinates(self):
        return self.__coordinates

    def getAncestorLand(self):
        """
        Returns the Ancestor Land for the Entertainment
        """
        authentication = get_header()
        try:
            if self.checkRelatedLocations():
                s = requests.get(self.__data['relatedLocations']['primaryLocations'][0]['links']['self']['href'], headers=authentication)
                data = json.loads(s.content)

                return data['links']['ancestorLand']['title'].replace("-"," ").replace(u"\u2013", " ").replace("'","")
            else:
                return None
        except:
            return None

    def checkRelatedLocations(self):
        """
        Returns true if it has related locations, false if none
        """
        try:
            check = self.__data['relatedLocations']
            return True
        except:
            return False

    def getRelatedLocations(self):
        """
        Returns the related locations of the entertainment
        """
        locs = []
        try:
            if self.checkRelatedLocations():
                for loc in self.__data['relatedLocations']['primaryLocations']:
                    type = loc['facilityType']
                    loc_id = loc['links']['self']['href'].split('/')[-1]

                    if type == 'point-of-interest':
                        locs.append(PointOfInterest(loc_id))
                    else:
                        print('no class for {} at this time'.format(type))
            return locs
        except:
            return locs
