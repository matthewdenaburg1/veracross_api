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


import collections.abc
import datetime
import functools
import time

import dateutil.parser
import requests


__author__ = "Forrest Beck,  Matthew Denaburg"


def singleton(cls):
    """
    Make a class a Singleton class (only one instance)

    From https://realpython.com/primer-on-python-decorators/#creating-singletons
    """

    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        """Wrapper"""

        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)

        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    return wrapper_singleton


@singleton
class Veracross:
    """This singleton class provides an easy interface to the Veracross API"""

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

        :param limit_remaining: Count of API calls remaining from header
        X-Rate-Limit-Remaining
        :param limit_reset: Reset Timer from header X-Rate-Limit-Reset
        :return: None

        """
        self.rate_limit_remaining = int(limit_remaining)
        self.rate_limit_reset = int(limit_reset)

        if self.rate_limit_remaining == 1:
            time.sleep(self.rate_limit_reset + 1)

    def _cleanup_parameters(self, parameters):
        """cleanup parameters"""

        params = {}
        if not parameters:
            return params

        for key in parameters:
            if key == "updated_after":
                # if it's a string, try to parse to datetime
                if isinstance(parameters[key], str):
                    params[key] = dateutil.parser.parse(parameters[key])
                # if it's a date, convert to the right format.
                if isinstance(parameters[key], datetime.date):
                    params[key] = parameters[key].strftime("%Y-%m-%d")
                else:  # if we got here, can't parse, so skip the keyt
                    pass
            elif isinstance(parameters[key], collections.abc.Iterable):
                params[key] = ",".join(map(str, parameters[key]))
            else:
                params[key] = str(parameters[key])

        return params

    def pull(self, source, parameters=None):
        """
        Get Veracross data with pagination

        :param source: VC Source (households, facstaff, facstaff/99)
        :param parameters: Optional API parameters normally in GET request
        :return: records in a list of dictionaries
        """

        if not self.__session.auth:
            raise RuntimeError("Not connected.")

        url = f"{self.api_url}{source}.json"

        params = self._cleanup_parameters(parameters)
        response = self.__session.get(url, params=params)
        records = []

        if response.status_code == 200:
            page = 1
            pages = 1

            # if there are multiple pages
            if 'X-Total-Count' in response.headers:
                pages = int(response.headers['X-Total-Count']) // 100 + 1

            while page <= pages:
                records += response.json()
                page += 1
                self.set_timers(response.headers['X-Rate-Limit-Remaining'],
                                response.headers['X-Rate-Limit-Reset'])
                response = self.__session.get(f"{url}?page={page}", params=params)

        return records
