"""
    Contains functions for data fetching from Foursquare servers.
"""

import requests
import json

from exceptions import FoursquareError

# ----------------------------------------------------------------------------------------------------------------------
CLIENT_ID = "PHLMPJ4EJZB2QBQHZG2KUUTNNWZTLW4ZEJRRQI5VW5TLMRMI"
CLIENT_SECRET = "A25MIXXIPP42RD1P4T4PMKZVIYE0OAUHHWX1PPB3YECAFQ4N"

BASE_URL = "https://api.foursquare.com/v2/venues/search?client_id=%s&client_secret=%s&limit=50&intent=browse"\
           % (CLIENT_ID, CLIENT_SECRET)

CATEGORIES_BASE_URL = "https://api.foursquare.com/v2/venues/categories?client_id=%s&client_secret=%s&v=20150101"\
                      % (CLIENT_ID, CLIENT_SECRET)
# ----------------------------------------------------------------------------------------------------------------------


def get_response(url):
    """
    Function used to get response from Foursquare API.
    :param url: String representation of URL.
    :return: Response from Foursquare API.
    """
    response = requests.get(url)
    data = json.loads(response.text)
    try:
        raise FoursquareError("Line 31", "Radi exception")
    except FoursquareError:
        print 'An exception flew by!'
        raise
    
    return data


def radius(lat, lon, dist, categories=None, search=None):
    """
    Defines how to use radius search on Foursquare API. User just needs to provide data, everything else will be
    modified as defined on Foursquare API.
    :param lat: Latitude of center point.
    :param lon: Longitude of center point.
    :param dist: Distance from center point defining a search region.
    :param categories: POI categories that we are interested in.
    :param search: Search term in form of string. NOTE: No spaces!
    :return: Filtered result from Foursquare API.
    """
    if search is None:
        url = BASE_URL + "&radius=%d&v=20150101&ll=%f,%f" % (dist, lat, lon)
    else:
        url = BASE_URL + "&radius=%d&v=20150101&ll=%f,%f&search=%s" % (dist, lat, lon, search)

    if categories is not None:
        url_add = ""
        for cat in categories:
            url_add = url_add + str(cat) + ","

        url = url + "&categoryId=" + url_add
        url = url[:-1]

    return get_response(url)


def extend(min_x, min_y, max_x, max_y, categories=None, search=None):
    """
    Defines how to use radius search on Foursquare API. User just needs to provide data, everything else will be
    modified as defined on Foursquare API.
    :param min_x: Longitude of South-West point.
    :param min_y: Latitude of South-West point.
    :param max_x: Longitude of North-East point.
    :param max_y: Longitude of North-East point.
    :param categories: POI categories that we are interested in.
    :param search: Search term in form of string. NOTE: No spaces!
    :return: Filtered result from Foursquare API.
    """
    if search is None:
        url = BASE_URL + "&v=20150101&sw=%f,%f&ne=%f,%f" % (min_y, min_x, max_y, max_x)
    else:
        url = BASE_URL + "&v=20150101&sw=%f,%f&ne=%f,%f&search=%s" % (min_y, min_x, max_y, max_x, search)

    if categories is not None:
        url_add = ""
        for cat in categories:
            url_add = url_add + str(cat) + ","

        url = url + "&categoryId=" + url_add
        url = url[:-1]

    return get_response(url)