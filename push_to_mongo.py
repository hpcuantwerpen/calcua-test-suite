#! /usr/bin/python3
import os, json, sys
import requests
from urllib3.exceptions import InsecureRequestWarning


# first argument is the file to submit
# second argument is the endpoint
api_endpoint = 'reframe'
report_name = f'last-{os.getenv("VSC_INSTITUTE_CLUSTER")}'
if len(sys.argv) > 1:
    report_name = sys.argv[1]
    if len(sys.argv) > 2:
        api_endpoint = sys.argv[2]

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
with open(f'/apps/antwerpen/reframe/logs/reports/{report_name}.json') as json_file:
    content = json.loads(json_file.read())

for element in content["runs"]:
    for test in element["testcases"]:
        # self signed cert
        r = requests.post(f'https://service.antwerpen.vsc:27016/add_{api_endpoint}/', json=test, verify=False)
        # if test["perfvars"] is not None:
        #     pass
