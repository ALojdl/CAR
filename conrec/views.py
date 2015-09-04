import json
import hashlib

from django.http import HttpResponse
from django.views.generic import View
from conrec.toolbox import get_recommendation
from conrec.controller import test_controller


# Recommend view, used as interface for users. It's connected only with recommend controller [controller.py].
class Recommend(View):
    def get(self, request):
        if 'uuid' in self.request.GET and 'matrix' in self.request.GET and 'lon' in self.request.GET and 'lat' in \
                self.request.GET and 'ts' in self.request.GET:
            matrix = self.request.GET['matrix']
            uuid = self.request.GET['uuid']
            lon = float(self.request.GET['lon'])
            lat = float(self.request.GET['lat'])
            ts = int(self.request.GET['ts'])
        else:
            response = HttpResponse("Insufficient data provided.")
            response.status_code = 400
            return response

        if 'ignore' in self.request.GET:
            ignore = self.request.GET['ignore']
        else:
            ignore = 'None'

        if 'number' in self.request.GET:
            number = int(self.request.GET['number'])
        else:
            number = 5

        dict_res = get_recommendation(matrix, ts, {'lat': lat, 'lon': lon}, uuid, ignore, number)
        response = HttpResponse(json.dumps(dict_res), content_type="application/json")
        response.status_code = 200
        return response

    def post(self, request):
        data = 'Use GET method instead.'
        response = HttpResponse(data)
        response.status_code = 200
        return response


class Test(View):
    def get(self, request):
        result = test_controller()
        return HttpResponse(json.dumps(result), content_type="application/json")
# ----------------------------------------------------------------------------------------------------------------------

class Categories(View):
    def get(self, request):
        categories = get_subcategories()
        return HttpResponse(json.dumps(categories), content_type="application/json")


class Matrix(View):
    def post(self, request):
        recommendation_matrix = request.body
        checksum = hashlib.md5()
        checksum.update(recommendation_matrix)
        response_data = checksum.hexdigest()

        recommendation_matrix.replace("'", '"')
        rm = RecommendationMatrix(name=response_data, data=recommendation_matrix)
        rm.save()

        response = HttpResponse(response_data)
        response.status_code = 200
        return response


class Activity(View):
    def get(self, request):
        if 'user' in self.request.GET:
            activity = get_user_activity(self.request.GET['user'])
        else:
            activity = "No user ID defined!"
        response = HttpResponse(activity)
        response.status_code = 200
        return response