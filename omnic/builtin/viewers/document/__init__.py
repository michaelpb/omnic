import os
import json

from omnic.web import viewer

PACKAGE_DIR = os.path.join(os.path.dirname(__file__), 'node_package')
PACKAGE_JSON_PATH = os.path.join(PACKAGE_DIR, 'package.json')

package_json = json.load(open(PACKAGE_JSON_PATH))


class PDFViewer(viewer.Viewer):
    types = [
        'PDF',
        'application/pdf',
    ]
    name = package_json['name']
    asset_dir = PACKAGE_DIR
    assets = []
    node_package = 'file:%s' % PACKAGE_DIR
