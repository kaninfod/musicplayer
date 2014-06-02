import requests
import re
import json

class api():
    def api_get(self, resource="", data="", where={}, embedded={}, page="", sort={}):
        if data:
            data = dict([(k, self.sanitize(v)) for k,v in data.items()])
            data = json.dumps(data)

        if where:
            where = dict([(k, self.sanitize(v)) for k,v in where.items()])
            where = "where=" + json.dumps(where)
            data = "%s&%s" % (data, where)

        if embedded:
            embedded = "embedded=" + json.dumps(embedded)
            data = "%s&%s" % (data, embedded)

        if sort:
            sort = "sort=" + sort
            data = "%s&%s" % (data, sort)

        if page:
            page = "page=%s" % page
            data = "%s&%s" % (data, page)

        data = data.lstrip("&")

        try:
            res = requests.get(url=resource, params=data)
        except:
            print(resource, "GET", data)
        else:
            return json.loads(res.text)

    def api_post(self, resource, data={}):
        #data = dict([(k, self.sanitize(v)) for k, v in data.items()])
        try:
            res = requests.post(url=resource, data=data)
        except:
            print(resource, "POST", data)
        else:
            return json.loads(res.text)

    def api_update(self, resource, etag, data):
        header = {"If-Match": etag, "Content-Type": "application/x-www-form-urlencoded"}
        data = dict([(k, self.sanitize(v)) for k, v in data.items()])
        try:
            res = requests.patch(resource, headers=header, data=data)
        except:
            print(resource, "PATCH", data)
        else:
            return res


    def sanitize(self ,s):

        s = re.compile('&').sub('%26', s)
        s = re.compile('#').sub('%23', s)
        s = re.compile('\$').sub('%24', s)
        s = re.compile('\+').sub('%2B', s)
        s = re.compile(',').sub('%2C', s)
        s = re.compile('/').sub('%2F', s)
        s = re.compile(':').sub('%3A', s)
        s = re.compile(';').sub('%3B', s)
        s = re.compile('=').sub('%3D', s)
        s = re.compile('\?').sub('%3F', s)
        s = re.compile('@').sub('%40', s)

        return s

    


ENTRY_POINT = "http://127.0.0.1:5000"




