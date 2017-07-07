import os
import json

PACKAGE_DIR = os.path.dirname(__file__)
PACKAGE_JSON_PATH = os.path.join(PACKAGE_DIR, 'package.json')

with open(PACKAGE_JSON_PATH) as fd:
    package_json = json.load(fd)

types = package_json['omnic']['types']
name = package_json['name']
asset_dir = PACKAGE_DIR
assets = []
node_package = 'file:%s' % PACKAGE_DIR
