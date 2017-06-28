import os

from omnic.web import viewer


class PDFViewer(viewer.Viewer):
    views = [
        'PDF',
        'application/pdf',
    ]
    asset_dir = os.path.join(os.path.dirname(__file__), 'js')
    assets = [
        'index.js',
        'package.json',
    ]
