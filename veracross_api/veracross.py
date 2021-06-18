"""
Veracross API Class

This class provides an easy interface to the Veracross API for python.

Rate limiting and pagination will be handled automatically.

Example of usage:

c = {
    'school_short_name': 'abc',
    'vcuser': 'username',
    'vcpass': 'password'
}

import veracross_api as v
vc = Veracross(c)
data = vc.pull("facstaff")
print(data)
data = vc.pull("facstaff/99999")
print(data)
param = {"updated_after": "2019-01-01"}
data = vc.pull("facstaff", parameters=param)
print(data)

Returned will be a dictionary of data.
"""


from urllib import parse
import math
import time

import requests


__author__ = "Forrest Beck,  Matthew Denaburg"


class Veracross:
    """This singleton class provides an easy interface to the Veracross API"""

    __instance = None

    def __new__(cls, config):
        """this makes the class a singleton"""

        if Veracross.__instance:
            return Veracross.__instance
        super().__init__(config)
        return Veracross.__instance

    def __init__(self, config):
        self.rate_limit_remaining = 300
        self.rate_limit_reset = 0
        self.__session = requests.Session()

        if 'school_short_name' in config:
            self.school_short_name = str(config['school_short_name'])
            self.api_url = 'https://api.veracross.com/{}/v2/'.format(self.school_short_name)

        if 'vcurl' in config:
            self.api_url = config['vcurl']

        if 'vcuser' in config and 'vcpass' in config:
            self.vcuser = config['vcuser']
            self.__session.auth = (config['vcuser'], config['vcpass'])
        else:
            raise KeyError('Credentials not provided')

        Veracross.__instance = self

    def __eq__(self, other):
        if id(self) == id(other):
            print("id")
            return True
        if not isinstance(other, Veracross):
            return False
        return self.vcuser == other.vcuser and self.api_url == other.api_url

    def __repr__(self):
        return f"VC API connected to {self.api_url} as {self.vcuser}"

    def set_timers(self, limit_remaining, limit_reset):
        """
        Sets the rate limits

        :param limit_remaining: Count of API calls remaining from header X-Rate-Limit-Remaining
        :param limit_reset: Reset Timer from header X-Rate-Limit-Reset
        :return: None

        """
        self.rate_limit_remaining = int(limit_remaining)
        self.rate_limit_reset = int(limit_reset)

        if self.rate_limit_remaining == 1:
            time.sleep(self.rate_limit_reset + 1)

    def pull(self, source, parameters=None):
        """
        Get Veracross data with pagination

        :param source: VC Source (households, facstaff, facstaff/99)
        :param parameters: Optional API parameters normally in GET request
        :return: records in a list of dictionaries
        """

        if not self.__session.auth:
            raise RuntimeError("Not connected.")

        if parameters is not None:
            s = f"{self.api_url}{source}.json?" + parse.urlencode(parameters, safe=':-,')
        else:
            s = f"{self.api_url}{source}.json"

        r = self.__session.get(s)
        records = []

        if r.status_code == 200:
            if 'X-Total-Count' in r.headers:  # if there are multiple pages
                pages = math.ceil(int(r.headers['X-Total-Count']) / 100)
            else:  # just return the results
                self.set_timers(r.headers['X-Rate-Limit-Remaining'],
                                r.headers['X-Rate-Limit-Reset'])
                return r.json()

            page = 1

            while page <= pages:
                self.set_timers(r.headers['X-Rate-Limit-Remaining'],
                                r.headers['X-Rate-Limit-Reset'])
                if parameters is None:
                    r = self.__session.get(s + "?page=" + str(page))
                else:
                    r = self.__session.get(s + "&page=" + str(page))

                records += r.json()
                page += 1

        return records
