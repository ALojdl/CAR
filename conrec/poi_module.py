"""
    This file contains different mathematical/geographical functions used in recommendation process.
"""
import urllib2
import json

from threading import Thread
from math import radians, cos, sin, atan2, sqrt, ceil, pi, floor
from models import Area

# Global variables
EARTH_RADIUS = 6371500
EARTH_CIRCUMFERENCE = EARTH_RADIUS * pi * 2
EARTH_CIRCUMFERENCE_1_2 = EARTH_CIRCUMFERENCE / 2
EARTH_CIRCUMFERENCE_1_4 = EARTH_CIRCUMFERENCE / 4

RADIUS = 300

REC_W = RADIUS
REC_H = RADIUS

LAT_ID_MAX = ceil(EARTH_CIRCUMFERENCE_1_4 / REC_H)
LON_ID_MAX = ceil(EARTH_CIRCUMFERENCE_1_2 / REC_W)

POI_DP_URL = "http://localhost/poi_dp/"


class GetFoursquareResponses(Thread):
    """
    This class is representing one thread sending request to Foursquare API. Threads do following:
        - make a request to Foursquare API
        - transforms given data to already defined format
        - stores the data as some element to list
    """
    def __init__(self, matrix_name, category, ne_lat, ne_lng, sw_lat, sw_lng):
        self.results = []
        self.matrix_name = matrix_name
        self.key = category['name']
        self.category_list = category['foursquare']
        self.ne_lat = ne_lat
        self.ne_lng = ne_lng
        self.sw_lat = sw_lat
        self.sw_lng = sw_lng
        super(GetFoursquareResponses, self).__init__()

    def run(self):
        raw_data = extend(self.sw_lng, self.sw_lat, self.ne_lng, self.ne_lat, self.category_list)

        for row in raw_data:
            info = {"fw_core": {"location": {"wgs84": {"latitude": row['geometry']['coordinates'][1],
                                                       "longitude": row['geometry']['coordinates'][0]}},
                                "category": self.matrix_name,
                                "name": {"": row['properties']['name']},
                                "short_name": {"": row['properties']['category']},
                                "label": {"": self.key},
                                "source": "foursquare"
                                }
                    }
            self.results.append(info)


class GetGivenRectangles(Thread):
    """
    This class represents thread requesting POIs for given area. Threads do following:
        - get South-West and North-East coordinates for the given rectangle
        - made call to get_points_ne_sw, where parameters are given coordinates
        - write info to database, that the given Area is stored
    """
    def __init__(self, matrix_name, categories, area_id):
        self.results = []
        self.matrix_name = matrix_name
        self.area_id = area_id
        self.categories = categories
        super(GetGivenRectangles, self).__init__()

    def run(self):
        sw_ne = get_sw_ne(self.area_id)
        self.results.append(
            get_points_ne_sw(sw_ne['ne']['lat'], sw_ne['ne']['lng'],
                             sw_ne['sw']['lat'], sw_ne['sw']['lng'],
                             self.categories, self.matrix_name)
        )

        # Store given rectangle as existing to database.
        Area(name=self.matrix_name, lat_id=self.area_id['lat'], lng_id=self.area_id['lng']).save()


def distance_between_gps_coordinates(lat_a, lon_a, lat_b, lon_b):
    """
    Calculate the distance in meters between two GPS points.
    :param lat_a: Latitude of point A.
    :param lon_a: Longitude of point A.
    :param lat_b: Latitude of point B.
    :param lon_b: Longitude of point B.
    :return: Distance between two given points in meters.
    """
    d_lon = radians(lon_b - lon_a)
    d_lat = radians(lat_b - lat_a)
    a = ((sin(d_lat/2)) ** 2) + cos(radians(lat_a)) * cos(radians(lat_b)) * ((sin(d_lon/2)) ** 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return EARTH_RADIUS * c


def grade_distance(lat_a, lng_a, lat_b, lng_b):
    """
    Gives grades for every distance, smaller distance gives better grade.
    :param lat_a: Latitude of point A.
    :param lng_a: Longitude of point A.
    :param lat_b: Latitude of point B.
    :param lng_b: Longitude of point B.
    :return: Returns grade for given distance.
    """
    dist = distance_between_gps_coordinates(lat_a, lng_a, lat_b, lng_b)
    if dist <= 10:
        return 5
    elif dist <= 50:
        return 3
    elif dist <= 200:
        return 2
    else:
        return 1


def get_id(coordinates):
    """
    Coordinates are processed and based on them function returns identification for this coordinates.
    :param coordinates: Dictionary on latitude and longitude coordinates of given point.
    :return: Dictionary of latitude and longitude identification numbers for processed rectangle.
    """
    lat_id = floor(EARTH_CIRCUMFERENCE_1_4 * coordinates['lat'] / 90 / REC_H)
    lat = 90 * lat_id / EARTH_CIRCUMFERENCE_1_4 * REC_H
    lng_id = floor(EARTH_CIRCUMFERENCE_1_2 * cos(radians(lat)) * coordinates['lng'] / 180 / REC_W)
    return {'lat': lat_id, 'lng': lng_id}


def get_sw_ne(db_id):
    """
    Based on rectangle identification, function returns South-West and North-East points describing that rectangle.
    :param db_id: Rectangle identification dictionary, containing two numbers.
    :return: Dictionary containing two coordinate dictionaries.
    """
    lat_s = 90 * db_id['lat'] / EARTH_CIRCUMFERENCE_1_4 * REC_H
    lng_w = 180 * db_id['lng'] / (EARTH_CIRCUMFERENCE_1_2 * cos(radians(lat_s))) * REC_W
    lat_n = 90 * (db_id['lat'] + 1) / EARTH_CIRCUMFERENCE_1_4 * REC_H
    lng_e = 180 * (db_id['lng'] + 1) / (EARTH_CIRCUMFERENCE_1_2 * cos(radians(lat_s))) * REC_W
    return {'sw': {'lat': lat_s, 'lng': lng_w}, 'ne': {'lat': lat_n, 'lng': lng_e}}


def distance(point_a, point_b):
    """
    Calculates distance between two GPS points described with two dictionaries.
    :param point_a: Dictionary containing latitude and longitude of given point.
    :param point_b: Dictionary containing latitude and longitude of given point.
    :return: Distance between points in meters.
    """
    d_lng = radians(point_b['lng'] - point_a['lng'])
    d_lat = radians(point_b['lat'] - point_a['lat'])
    a = sin(d_lat/2)**2 + cos(radians(point_a['lat'])) * cos(radians(point_b['lat'])) * sin(d_lng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return EARTH_RADIUS * c


def center(rect):
    """
    Calculate coordinates of central point inside given rectangle.
    :param rect: Dictionary representing North-East and South-West points of given rectangle area.
    :return: Dictionary (containing latitude and longitude) describing central point of given rectangle area.
    """
    return {'lat': (rect['sw']['lat'] + rect['ne']['lat']) / 2, 'lng': (rect['sw']['lng'] + rect['ne']['lng']) / 2}


def get_ids(coordinates):
    """
    For given coordinates returns rectangle identification dictionaries that are candidates for circle intersection.
    :param coordinates: Dictionary containing latitude and longitude of some point.
    :return: List of dictionaries that represent nine rectangles that are candidates for circle intersection.
    """
    size = int(ceil(float(RADIUS) / min(REC_H, REC_W)))
    ids = []
    center_id = get_id(coordinates)
    center_sq = get_sw_ne(center_id)

    lat_dh = (center_sq['ne']['lat'] - center_sq['sw']['lat']) / 2

    ids.append(center_id)
    for j in range(1, size + 1):
        # West
        identification = {'lat': center_id['lat'], 'lng': center_id['lng'] - j}
        sq = get_sw_ne(identification)
        if distance(coordinates, center(sq)) <= RADIUS:
            ids.append(identification)

        # East
        identification = {'lat': center_id['lat'], 'lng': center_id['lng'] + j}
        sq = get_sw_ne(identification)
        if distance(coordinates, center(sq)) <= RADIUS:
            ids.append(identification)

        top_sq = center_sq.copy()
        bot_sq = center_sq.copy()

    for i in range(0, size):
        top_id = get_id({'lat': top_sq['ne']['lat'] + lat_dh, 'lng': coordinates['lng']})
        bot_id = get_id({'lat': bot_sq['sw']['lat'] - lat_dh, 'lng': coordinates['lng']})
        top_sq = get_sw_ne(top_id)
        bot_sq = get_sw_ne(bot_id)
        if distance(coordinates, center(top_sq)) <= RADIUS:
            ids.append(top_id)

        if distance(coordinates, center(bot_sq)) <= RADIUS:
            ids.append(bot_id)

        for j in range(1, size + 1):
            # North-West
            identification = {'lat': top_id['lat'], 'lng': top_id['lng'] - j}
            sq = get_sw_ne(identification)
            if distance(coordinates, center(sq)) <= RADIUS:
                ids.append(identification)

            # North-East
            identification = {'lat': top_id['lat'], 'lng': top_id['lng'] + j}
            sq = get_sw_ne(identification)
            if distance(coordinates, center(sq)) <= RADIUS:
                ids.append(identification)

            # South-West
            identification = {'lat': bot_id['lat'], 'lng': bot_id['lng'] - j}
            sq = get_sw_ne(identification)
            if distance(coordinates, center(sq)) <= RADIUS:
                ids.append(identification)

            # South-East
            identification = {'lat': bot_id['lat'], 'lng': bot_id['lng'] + j}
            sq = get_sw_ne(identification)
            if distance(coordinates, center(sq)) <= RADIUS:
                ids.append(identification)
    return ids


def get_points_ne_sw(ne_lat, ne_lng, sw_lat, sw_lng, categories, matrix_name):
    """
    Function reads all POIs that are part of given categories and store them to list that is then returned.
    :param ne_lat: North-East latitude.
    :param ne_lng: North-East longitude.
    :param sw_lat: South-West latitude.
    :param sw_lng: South-West longitude.
    :param categories: Identification list of categories required.
    :returns result: List of result from all threads.
    """
    threads = []
    results = []
    for cat in categories:
        t = GetFoursquareResponses(matrix_name, cat, ne_lat, ne_lng, sw_lat, sw_lng)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
        for row in t.results:
            results.append(row)
    return results


def check_for_areas(area_list, name):
    """
    Check what area fields need to be stored to POI Data Provider, resulting in list of coordinates representing this
    areas.
    :param area_list: List of dictionaries, representing all areas needed for successful search to POI DP.
    :return: List of North-East and South-West points representing this areas.
    """
    lst_needed = []
    for area in area_list:
        if not Area.objects.filter(name=name, lat_id=area['lat'], lng_id=area['lng']).exists():
            lst_needed.append(area)
    return lst_needed


def store_to_areas(matrix_name, categories_list, area_id_list):
    """
    Function that stores information for given area identification. Based of this identification, function gets
    coordinates and then makes call to Foursquare API to collect data and store it to our local database.
    :param matrix_name: Name of matrix used to categories data.
    :param categories_list: List of categories defined in recommendation matrix.
    :param area_id_list: List of area identification numbers.
    """
    threads = []
    results = []
    for area_id in area_id_list:
        t = GetGivenRectangles(matrix_name, categories_list, area_id)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
        for lst in t.results:
            for row in lst:
                results.append(row)
    return results


def get_foursquare_categories():
    """
    Add Foursquare categories to database
    :return: content of Foursquare API response
    """
    request = urllib2.Request(CATEGORIES_BASE_URL, None)
    result = urllib2.urlopen(request, None, timeout=10)
    if result.code == 200:
        response = json.loads(result.read())
        return response['response']['categories']

    return None


def categories():
    """
    Reads Foursquare category hierarchy and sends second level of this hierarchy to user.
    :return: List containing dictionaries representing Foursquare subcategories.
    """
    categories = get_foursquare_categories()
    categories_lst = []
    for cat in categories:
        for sub_cat in cat['categories']:
            categories_lst.append({"name": sub_cat['name'], "id": sub_cat['id']})

    return categories_lst


def fetch_poi(matrix_name, categories_list, lat, lng, stretch):
    """
    Search for points of interest on poi data provider, for the given search radius.
    :param lat: Latitude of center point.
    :param lng: Longitude of center point.
    :param stretch: Search radius.
    :return: Returns points of interest database provider answer, dictionary of available points of interest in the
    given radius.
    """
    # Check which area field we need.
    lst_ids = get_ids({'lat': lat, 'lng': lng})

    # For given fields check which are not in database.
    needed_ids = check_for_areas(lst_ids, matrix_name)

    # For those that are not stored in database, call Foursquare and store data, for them.
    poi_list = store_to_areas(matrix_name, categories_list, needed_ids)

    # Make a search in Point od Interest Data Provider for POI-s in given radius.
    url = POI_DP_URL + ('/radial_search.php?lat=%f&lon=%f&radius=%d&category=%s' % (lat, lng, stretch, matrix_name))
    headers = dict()
    headers['Content-type'] = 'application/json'
    result = None
    read_list = []
    try:
        request = urllib2.Request(url, None, headers=headers)
        result = urllib2.urlopen(request, timeout=10).read()
    except:
        return dict()
    poi = json.loads(result)
    if 'pois' in poi and len(poi['pois']) > 0:
        read_list = poi['pois']
    else:
        read_list = dict()

    return [read_list, poi_list]