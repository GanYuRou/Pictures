import json

from django.http import HttpResponse

from pictures.utils.datetime_util import DatetimeEncoder


class ResponseUtil:

    @staticmethod
    def response_format(code, data):
        resp = ResponseUtil.gen_standard_response(code, data)
        return HttpResponse(json.dumps(resp), content_type='application/json, charset=utf-8')

    @staticmethod
    def response_orm(code, query_set):
        resp = json.dumps(ResponseUtil.gen_standard_response(code, list(query_set)), cls=DatetimeEncoder)
        return HttpResponse(resp, content_type='application/json, charset=utf-8')

    @staticmethod
    def gen_standard_response(code, data):
        return {
            'code': code,
            'data': data,
        }
