import os
import datetime
import pickle
import requests

class WeatherAPI(object):
    """
    This is a python wrapper for the Malaysian Weather Service API. 
    TO use this, first register an account(I wish this public project is really public)

    url at https://api.met.gov.my/
    """

    def __init__(self, api_key, end_point="https://api.met.gov.my/v2/", cache_dir=None):
        """
        api = WeatherAPI("API_KEY")
        """
        self.end_point = end_point
        self.headers = {
                "Authorization" : "METToken %s" % api_key
        }
        self.cache_dir = cache_dir
        self.cache, self.cache_index = {}, {}
        self.cache_expiry = datetime.timedelta(days=1)
        if self.cache_dir:
            self.load_cache()

    def cache_expire(self):
        now = datetime.datetime.now()
        for k, v in self.cache_index.items():
            if now - k >= self.cache_expiry:
                for c in v:
                    try:
                        del self.cache[c]
                    except:
                        pass

    def load_cache(self):
        try:
            with open(os.path.join(self.cache_dir, "cuaca.p"), "rb") as fp:
                self.cache = pickle.load(fp)
        except FileNotFoundError:
                pass
        try:
            with open(os.path.join(self.cache_dir, "cuacaidx.p"), "rb") as fp:
                self.cache_index = pickle.load(fp)
            self.cache_expire()
        except FileNotFoundError:
            pass

    def save_cache(self):
        if not self.cache_dir: return
        self.cache_expire()
        try:
            with open(os.path.join(self.cache_dir, "cuaca.p"), "wb") as fp:
                pickle.dump(self.cache, fp)
            with open(os.path.join(self.cache_dir, "cuacaidx.p"), "wb") as fp:
                pickle.dump(self.cache_index, fp)
        except:
            raise

    def forecast(self, location_id, start_date, end_date, forecast_type='GENERAL'):
        """
        Get a weather forecast from API

        Arguments:
            location_id - id of location use location method
            start_date  - Date in string, format is yyyy-mm-dd
            end_date    - Date in string, format is yyyy-mm-dd
        """
        # there is data type, but only forecast work :-/
        data_url = "{}/{}".format(self.end_point, "data")
        if forecast_type not in ('GENERAL', 'MARINE'):
            raise Exception("Error, forecast_type must be GENERAL or MARINE")
        params = {
            "datasetid":"FORECAST", # only this work for data url
            "datacategoryid": forecast_type,
            "locationid": location_id, 
            "start_date": start_date,
            "end_date": end_date
        }
        api_result = self.call_api(data_url, params)
        return api_result

    def locations(self, location_type):
        """
        GET a list of Locations id from API

        Arguments:
            location_type - string must be STATE, DISTRICT, TOWN, TOURISTDEST
        """
        location_url = "{}/{}".format(self.end_point, "locations")
        if location_type not in ("STATE", "DISTRICT", "TOWN", "TOURISTDEST", "WATERS"):
            raise Exception("Error, location type must be STATE, DISTRICT, TOWN, TOURISTDEST, WATERS")

        params = {
            "locationcategoryid": location_type
        }

        api_result = self.call_api(location_url, params)
        
        return api_result

    def location(self, location_name, location_type):
        """
        Get a single location id

        Arguments:
            location_name - name of location in string
            location_type - string must be STATE, DISTRICT, TOWN, TOURISTDEST, WATERS
        """
        locations = self.locations(location_type)
        location_id = None

        # Search result
        for location in locations:
            if location["name"] == location_name.upper():
                return location["id"]

        return location_id

    def state(self, name):
        """
        A wrapper for locations(name, "STATE")

        Arguments:
            name - name of location in string
        """
        # 1 line method suck in python, but the name of location id is obscure
        return self.location(name, "STATE")

    def district(self, name):
        return self.location(name, "DISTRICT")

    def town(self, name):
        return self.location(name, "TOWN")

    def states(self):
        return self.locations("STATE")

    def districts(self):
        return self.locations("DISTRICT")

    def towns(self):
        return self.locations("TOWN")

    def tourist_attractions(self):
        return self.locations("TOURISTDEST")

    def tourist_attraction(self, name):
        
        return self.location(name, "TOURISTDEST")

    def water(self, name):
        return self.location(name, "WATERS")

    def waters(self):
        return self.locations("WATERS")

    def datatypes(self):
        """
        GET a list of data types from API - to interpret the results from data
        endpoint
        """
        url = "{}/{}".format(self.end_point, "datatypes")
        return self.call_api(url)

    def call_api(self, url, params={}, metadata=False):
        """
        A utility fuction to make API call easy, wrap around requests
        """
        k = "{}{}".format(url, str(params))
        if k in self.cache:
            self.headers["If-None-Match"] = self.cache[k]["etag"]
        r = requests.get(url, headers=self.headers, params=params)
        # Should we maintain api result, metadata can be useful :-/
        if r.status_code == 200:
            etag = r.headers.get("ETag", None)
            data = r.json()
            if metadata:
                self.cache[k] = {"etag": etag, "result": data["metadata"]}
                self.cache_index[datetime.datetime.now()] = k
                return data["metadata"]
            # might fail
            self.cache[k] = {"etag": etag, "result": data["results"]}
            self.cache_index[datetime.datetime.now()] = k
            return data["results"]
        elif r.status_code == 304:
            return self.cache[k]["result"]

        return r.json()
