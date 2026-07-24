import urllib.request
import json

base = 'http://127.0.0.1:5000'

with urllib.request.urlopen(base + '/api/readings') as response:
    data = json.load(response)

assert isinstance(data, list) and len(data) >= 10, data

req = urllib.request.Request(base + '/api/simulate', data=json.dumps({'location': 'North Bank', 'device_id': 'NODE-01', 'water_level_m': 2.1}).encode(), headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as response:
    payload = json.load(response)

assert payload['ok'] is True, payload

print('verified', len(data), payload)
