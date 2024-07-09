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
    ('station_outdoor_humidity_pct', 'Outdoor Humidity, %', 'humidity'),
    ('station_outdoor_windgustmph_mph', 'Wind Gust Speed, MPH', 'windgustmph'),
    ('station_outdoor_maxdailygust_mph', 'Max Daily Wind Gust, MPH', 'maxdailygust'),
    ('station_outdoor_winddir_deg', 'Wind Direction, Degrees', 'winddir'),
    ('station_outdoor_uv_num', 'UV Index', 'uv'),
    ('station_outdoor_solarradiation_num', 'Solar Radiation, W/m²', 'solarradiation'),
    ('station_outdoor_hourlyrainin_in', 'Hourly Rainfall, in', 'hourlyrainin'),
    ('station_outdoor_eventrainin_in', 'Event Rainfall, in', 'eventrainin'),
    ('station_outdoor_dailyrainin_in', 'Daily Rainfall, in', 'dailyrainin'),
    ('station_outdoor_weeklyrainin_in', 'Weekly Rainfall, in', 'weeklyrainin'),
    ('station_outdoor_monthlyrainin_in', 'Monthly Rainfall, in', 'monthlyrainin'),
    ('station_outdoor_yearlyrainin_in', 'Yearly Rainfall, in', 'yearlyrainin'),
    ('station_outdoor_totalrainin_in', 'Total Rainfall, in', 'totalrainin'),
    ('station_outdoor_battout_num', 'Outdoor Battery Status', 'battout'),
    ('station_indoor_tempinf_f', 'Indoor Temperature, F', 'tempinf'),
    ('station_indoor_humidityin_pct', 'Indoor Humidity, %', 'humidityin'),
    ('station_outdoor_baromrelin_in', 'Relative Barometric Pressure, inHg', 'baromrelin'),
    ('station_outdoor_baromabsin_in', 'Absolute Barometric Pressure, inHg', 'baromabsin'),
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