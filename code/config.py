from json import load

with open('config.json') as f:
    cfg = load(f)

with open('network_creds.json') as f:
    cfg['network']['creds'] = load(f)
