"""Python wrapper for the Malaysian Weather Service API.

To use this, first register an account at https://api.met.gov.my/
(I wish this public project is really public)
"""
import os
import datetime
import pickle
import requests
import json

class WeatherAPI(object):
    """Weather API wrapper.

    >>> from cuaca
    >>> api = cuaca.api.WeatherAPI("API_KEY")
    """

    def __init__(self, api_key, end_point="https://api.met.gov.my/v2.1/", cache_dir=None, offset_size=50):
        self.end_point = end_point
        self.headers = {"Authorization": "METToken %s" % api_key}
        self.cache_expiry = datetime.timedelta(days=1)
        self.offset = offset_size
        if cache_dir:
            self.cache_file = os.path.join(cache_dir, "cuaca.p")
            self.cache = self._load_cache()
        else:
            self.cache = {}

    def __del__(self):  # XXX: Should we implement __exit__?
        self._save_cache()

    def _not_expired(self, d):
        """Return cache that are not expired."""
        return {k: d[k] for k in d if d[k]["expire"] > datetime.datetime.now()}

    def _load_cache(self):
        if not os.path.exists(getattr(self, 'cache_file', '')):
            return {}
        with open(self.cache_file, "rb") as f:
            return self._not_expired(pickle.load(f))

    def _save_cache(self):
        if not hasattr(self, 'cache_file'):
            return
        with open(os.path.join(self.cache_file), "wb") as f:
            pickle.dump(self._not_expired(self.cache), f)

    def _parse_warning(self, data):
        # data is list
        results = []
        for item in data:
            value = item["value"]
            print(value["text"].keys())
            print(value["text"]["en"])
            # because json parser hate single quote
            value = value.replace("'",'"')
            item["value"] = json.loads(value)
            results.append(item)
        return results


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
            "datasetid": "FORECAST",  # only this work for data url
            "datacategoryid": forecast_type,
            "locationid": location_id,
            "start_date": start_date,
            "end_date": end_date
        }
        api_result = self.call_api(data_url, params)
        return api_result

    def locations(self, location_type, page=0): # page always start with 0, 
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
        if page:
            params["offset"] = self.offset * page

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

    def stations(self):
        station_url = "{}/{}".format(self.end_point, "stations")
        return self.call_api(station_url)

    def warning(self, datacategoryid, start_date, end_date):
        accepted_cat = ("QUAKETSUNAMI2", "WINDSEA2", "THUNDERSTORM2", "RAIN2", "CYCLONE2")
        if datacategoryid not in accepted_cat:
            raise Exception("datacategoryid must be QUAKETSUNAMI2 or WINDSEA2 or THUNDERSTORM2 or RAIN2 or CYCLONE2")
        url = "{}/{}".format(self.end_point, "data")

        params = {
            "datasetid": "WARNING",
            "datacategoryid": datacategoryid,
            "start_date": start_date,
            "end_date": end_date
        }
        data = self.call_api(url, params)
        # data value is string, convert it into json to make it easier
        # Also allow opportunity to work on the text to extract thing
        return data

    def call_api(self, url, params={}, metadata=False):
        """Wrapper to provide easy access to API call."""
        k, now = "{}{}".format(url, str(params)), datetime.datetime.now()
        if k in self.cache and self.cache[k]["expire"] > now:
            self.headers["If-None-Match"] = self.cache[k]["etag"]

        r = requests.get(url, headers=self.headers, params=params)
        # Should we maintain api result, metadata can be useful :-/
        if r.status_code == 200:
            data = r.json()
            self.cache[k] = {
                "etag": r.headers.get("ETag", None),
                "result": data["metadata"] if metadata else data["results"],
                "expire": datetime.datetime.now() + self.cache_expiry}
            return self.cache[k]["result"]
        elif r.status_code == 304:
            return self.cache[k]["result"]

        return r.json()
