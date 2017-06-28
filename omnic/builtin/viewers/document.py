import os

from omnic.web import viewer


class PDFViewer(viewer.Viewer):
    views = ['PDF']
    asset_dir = os.path.join(__file__, 'js')
    assets = [
        'index.js',
        'package.json',
    ]
