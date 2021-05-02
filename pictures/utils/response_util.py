import json
from django.http import HttpResponse


class ResponseUtil:

    @staticmethod
    def response_format(code, data):
        resp = {
            'code': code,
            'data': data,
        }
        return HttpResponse(json.dumps(resp), content_type='application/json, charset=utf-8')
