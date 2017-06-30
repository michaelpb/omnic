'''
A read-only admin interface that is useful for monitoring broad server stats
and testing conversions.
'''
import json
from urllib.parse import urlencode

from omnic import singletons
from omnic.responses.template import Jinja2TemplateHelper
from omnic.types.resource import ForeignResource

templates = Jinja2TemplateHelper('omnic.builtin.services.admin', 'templates')

FORM_DEFAULT = {
    'res_url': 'unsplash.it/500/500',
    'thumb_width': 200,
    'thumb_height': 200,
    'viewer_type': '',
}


def _gen_thumb_src(form):
    qs = urlencode({'url': form['res_url']})
    ts = 'thumb.jpg:%sx%s' % (form['thumb_width'], form['thumb_height'])
    return 'http://localhost:8080/media/%s/?%s' % (ts, qs)


def _gen_viewer_src(form):
    viewer_type = form['viewer_type'].strip()
    if not viewer_type:
        return ''
    # For now, we just go by type, not URL
    # qs = urlencode({'url': form['res_url']})
    # return 'http://localhost:8080/media/%s/?%s' % (viewer_type, qs)
    return viewer_type


def _depluralize_query_dict(dct):
    return {key: value[0] for key, value in dct.items()}


async def get_worker_info():
    workers = [
        {
            'queue_size': worker.queue_size(),
            'dequeued': worker.stats_dequeued,
            'success': worker.stats_success,
            'began': worker.stats_began,
            'error': worker.stats_error,
            'number': num,
        }
        for num, worker in enumerate(singletons.workers)
    ]

    # Await all queue_size coros (python syntax does not support this in
    # array comprehension)
    # NOTE: For some reason, not working
    # for worker in workers:
    #     worker['queue_size'] = await worker['queue_size']

    return workers


def get_nodes_edges_ids(ext=None):
    dgraph = singletons.converter_graph.dgraph
    paths_flat = None
    if ext is not None:
        paths = dgraph.get_all_paths_from(ext)
        path_list = [item for item in (path for cost, path in paths)]
        paths_flat = frozenset(sum(path_list, tuple()))
    nodes = []
    edges = []
    all_node_set = set()
    for a, a_edges in dgraph.edges.items():
        for b in a_edges.keys():
            all_node_set.add(a)
            all_node_set.add(b)

    # Clean up node set
    node_set = set()
    for node in all_node_set:
        if paths_flat:
            if node not in paths_flat:
                continue
        if '/' in node:
            continue
        node_set.add(node)

    idified = {}
    id_to_ext = {}
    converters = singletons.converter_graph.converter_list
    for i, node in enumerate(node_set):
        idified[node] = i
        id_to_ext[i] = node
        group = -1
        # Identify which converters for each node
        for num, converter in enumerate(converters):
            if node in converter.inputs:
                group = num
                break
        nodes.append({
            'id': i,
            'label': node,
            'group': group,
        })

    for a, a_edges in dgraph.edges.items():
        for b in a_edges.keys():
            if a in idified and b in idified:
                # skip over mimetypes
                edges.append({
                    'from': idified[a],
                    'to': idified[b],
                    'arrows': 'to',
                })
    return nodes, edges, id_to_ext


async def conversion_tester_root(request):
    redirect = singletons.server.response.redirect
    return redirect('/admin/conversion/')


async def conversion_tester(request):
    singletons.settings
    workers = await get_worker_info()

    form = {}
    form.update(FORM_DEFAULT)
    form.update(_depluralize_query_dict(request.args))
    thumb_src = _gen_thumb_src(form)
    viewer_src = _gen_viewer_src(form)

    # Determine type
    ext = None
    url_string = 'http://%s' % form['res_url']
    try:
        foreign_res = ForeignResource(url_string)
    except:
        pass  # could be a myriad of errors
    else:
        if foreign_res.cache_exists():
            # Determine the file type of the foreign resource
            typed_foreign_res = foreign_res.guess_typed()
            ext = typed_foreign_res.typestring.extension

    return templates.render(request, 'index.html', {
        'is_conversion': True,
        'workers': workers,
        'thumb_src': thumb_src,
        'viewer_src': viewer_src,
        'form': form,
        'ext': ext,
    })


async def conversion_graph_root(request):
    return await conversion_graph(request, None)


async def conversion_graph(request, ext):
    nodes, edges, id_to_ext = get_nodes_edges_ids(ext)

    return templates.render(request, 'graph.html', {
        'is_graph': True,
        'nodes_json': json.dumps(nodes, indent=2),
        'edges_json': json.dumps(edges, indent=2),
        'id_to_ext_json': json.dumps(id_to_ext, indent=2),
        'ext': ext if ext else '*',
    })


async def poll_worker_queue(request):
    workers = await get_worker_info()
    return templates.render(request, 'workers.html', {
        'workers': workers,
    })
