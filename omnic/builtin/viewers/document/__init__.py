import os

from omnic.web import viewer


class PDFViewer(viewer.Viewer):
    types = [
        'PDF',
        'application/pdf',
    ]
    name = 'pdf_viewer'
    asset_dir = os.path.join(os.path.dirname(__file__), 'js')
    assets = []
    node_package = 'file:%s' % asset_dir
