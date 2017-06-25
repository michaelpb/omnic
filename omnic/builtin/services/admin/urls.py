from . import views

urls = {
    '': views.conversion_tester_root,
    'conversion/': views.conversion_tester,
    'graph/': views.conversion_graph_root,
    'graph/<ext>/': views.conversion_graph,
    'ajax/workers/': views.poll_worker_queue,
}
