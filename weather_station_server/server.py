import time

from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})
REQUEST_COUNT = Counter(
    'app_request_count',
    'Application Request Count',
    ['method', 'endpoint', 'http_status']
)
REQUEST_LATENCY = Histogram(
    'app_request_latency_seconds',
    'Application Request Latency',
    ['method', 'endpoint']
)

GAUGE_DEFS = [
    ('station_outdoor_temp_f', 'Outdoor Temperature, F', 'tempf'),
    ('station_outdoor_windspeed_mph', 'Wind Speed, MPH', 'windspeedmph'),
]

GAUGES = {
    ws_name: Gauge(
        prom_name,
        prom_desc,
    ) for prom_name, prom_desc, ws_name in GAUGE_DEFS
}

@app.route('/')
def hello():
    start_time = time.time()
    REQUEST_COUNT.labels('GET', '/', 200).inc()
    response = jsonify(message='Hello, world!')
    REQUEST_LATENCY.labels('GET', '/').observe(time.time() - start_time)
    return response

@app.route('/data/report/')
def report():
    for ws_name, gauge in GAUGES.items():
        print(f'reading {ws_name}')
        value = float(request.args.get(ws_name))
        gauge.set(value)

    return 'ok'