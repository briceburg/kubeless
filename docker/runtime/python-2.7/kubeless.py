#!/usr/bin/env python

import sys
import os
import imp

from bottle import route, run, request

from prometheus_client import generate_latest, REGISTRY, Gauge, Counter

IN_PROGRESS = Gauge("inprogress_requests", "help")
REQUESTS = Counter('http_requests_total', 'Kubeless function calls', ['method', 'endpoint'])

mod_name = os.getenv('MOD_NAME')
func_handler = os.getenv('FUNC_HANDLER')

mod_path = '/kubeless/' + mod_name + '.py'

try:
    mod = imp.load_source('lambda', mod_path)
except ImportError:
    print("No valid module found for the name: lambda, Failed to import module")

@IN_PROGRESS.track_inprogress()
@route('/', method="GET")
def handler():
    REQUESTS.labels(method="GET", endpoint="handler").inc()
    return getattr(mod, func_handler)()

@IN_PROGRESS.track_inprogress()
@route('/', method="POST")
def post_handler():
    REQUESTS.labels(method="POST", endpoint="post_handler").inc()
    return getattr(mod, func_handler)(request)

@route('/healthz', method="GET")
def healthz():
    return "OK"

@IN_PROGRESS.track_inprogress()
@route('/metrics')
def metrics():
    return generate_latest(REGISTRY)

run(host='0.0.0.0', port=8080)
