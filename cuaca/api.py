import requests


class WeatherAPI(object):
    """
    This is a python wrapper for the Malaysian Weather Service API. 
    TO use this, first register an account(I wish this public project is really public)

    url at https://api.met.gov.my/
    """

    def __init__(self, api_key, end_point="https://api.met.gov.my/v2/"):
        """
        api = WeatherAPI("API_KEY")
        """
        self.end_point = end_point
        self.headers = {
                "Authorization" : "METToken %s" % api_key
        }

    def forecast(self, location_id, start_date, end_date):
        """
        Get a weather forecast from API

        Arguments:
            location_id - id of location use location method
            start_date  - Date in string, format is yyyy-mm-dd
            end_date    - Date in string, format is yyyy-mm-dd
        """
        # there is data type, but only forecast work :-/
        data_url = "{}/{}".format(self.end_point, "data")
        params = {
            "datasetid":"FORECAST", # only this work for data url
            "datacategoryid": "GENERAL", # only this work :-/
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
        if location_type not in ("STATE", "DISTRICT", "TOWN", "TOURISTDEST"):
            raise Exception("Error, location type must be STATE, DISTRICT, TOWN, TOURISTDEST")

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
            location_type - string must be STATE, DISTRICT, TOWN, TOURISTDEST
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

    def call_api(self, url, params, metadata=False):
        """
        A utility fuction to make API call easy, wrap around requests
        """
        r = requests.get(url, headers=self.headers, params=params)
        # Should we maintain api result, metadata can be useful :-/
        if r.status_code == 200:
            data = r.json()
            if metadata:
                return data["metadata"]
            # might fail
            return data["results"]

        return r.json()

