"""
Hover Client

Wraper for hover API based on https://gist.github.com/dankrause/5585907

"""

import requests
import sys


class HoverException(Exception):
    pass


class HoverClient(object):
    def __init__(self, username, password, domain_name):

        params = {"username": username, "password": password}
        r = requests.post("https://www.hover.com/api/login", params=params)

        if not r.ok or "hoverauth" not in r.cookies:
            raise HoverException(r)
        self.cookies = {"hoverauth": r.cookies["hoverauth"]}

        dns = self.call("get", "dns")
        self.domain = None

        for domain in dns["domains"]:
            if domain["domain_name"] == domain_name:
                self.domain = domain

        if self.domain is None:
            raise HoverException("Domain not found")

    @property
    def dns_id(self):
        return self.domain["id"]

    def call(self, method, resource, data=None):
        url = "https://www.hover.com/api/{0}".format(resource)
        r = requests.request(method, url, data=data, cookies=self.cookies)

        if not r.ok:
            raise HoverException(r)
        if r.content:
            body = r.json()
            if "succeeded" not in body or body["succeeded"] is not True:
                raise HoverException(body)
            return body

    def add_record(self, type, name, content):
        record = {"name": name, "type": type, "content": content}
        return self.call("post", "domains/{0}/dns".format(self.dns_id), record)

    def remove_record(self, type, name):

        records = self.call("get", "domains/{0}/dns".format(self.dns_id))["domains"][0]["entries"]

        for record in records:
            if record["type"] == type and record["name"] == name:
                return self.call("delete", "dns/{0}".format(record["id"]))

        raise HoverException("Record not found")
