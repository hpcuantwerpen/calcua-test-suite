#! /usr/bin/python3
import os, json, sys
import requests
from urllib3.exceptions import InsecureRequestWarning


# first argument is the file to submit
# second argument is the endpoint
api_endpoint = 'reframe'
logdir = os.getenv('CALCUA_LOGDIR', '/apps/antwerpen/reframe/logs').rstrip('/')   # same default as calcua_config.py
cluster = os.getenv('VSC_INSTITUTE_CLUSTER')
report_name = f'last-{cluster}'
if len(sys.argv) > 1:
    report_name = sys.argv[1]
    if len(sys.argv) > 2:
        api_endpoint = sys.argv[2]
elif not cluster:
    sys.exit('VSC_INSTITUTE_CLUSTER is not set: pass the report name, e.g. ./push_to_mongo.py last-vaughan')

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
with open(f'{logdir}/reports/{report_name}.json') as json_file:
    content = json.loads(json_file.read())

failed = 0
for element in content["runs"]:
    for test in element["testcases"]:
        # self signed cert
        r = requests.post(f'https://service.antwerpen.vsc:27016/add_{api_endpoint}/', json=test, verify=False)
        if not r.ok:
            failed += 1
            print(f'{test.get("display_name", test.get("name"))}: HTTP {r.status_code} {r.text[:200]}', file=sys.stderr)
        # if test["perfvars"] is not None:
        #     pass

if failed:
    print(f'{failed} test case(s) rejected', file=sys.stderr)
    sys.exit(1)
