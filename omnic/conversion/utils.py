from omnic import singletons
from omnic.types.resource import (ForeignResource, TypedForeignResource,
                                  TypedLocalResource, TypedPathedLocalResource,
                                  TypedResource)
from omnic.types.typestring import TypeString
from omnic.utils.iters import first_last_iterator


def _just_checking_response(resource_exists, resource):
    response = singletons.server.response
    return response.json({
        'url': resource.url_string,
        'ready': resource_exists,
    })


async def convert_endpoint(url_string, ts, is_just_checking, custom_profiles=None):
    '''
    Main logic for HTTP endpoint.
    '''
    response = singletons.server.response

    # Prep ForeignResource and ensure does not validate security settings
    singletons.settings
    foreign_res = ForeignResource(url_string)

    target_ts = TypeString(ts)
    target_resource = TypedResource(url_string, target_ts)

    # Send back cache if it exists
    if target_resource.cache_exists():
        if is_just_checking:
            return _just_checking_response(True, target_resource)
        return await response.file(target_resource.cache_path, headers={
            'Content-Type': target_ts.mimetype,
        })

    # Check if already downloaded. If not, queue up download.
    if not foreign_res.cache_exists():
        singletons.workers.enqueue_download(foreign_res)

    # Queue up a single function that will in turn queue up conversion
    # process
    singletons.workers.enqueue_sync(
        enqueue_conversion_path,
        url_string,
        str(target_ts),
        singletons.workers.enqueue_convert,
        custom_profiles,
    )

    if is_just_checking:
        return _just_checking_response(False, target_resource)

    # Respond with placeholder
    return singletons.placeholders.stream_response(target_ts, response)

async def cache_foreign_resource(url_string):
    '''
    Resolve a foreign resource to cache.
    '''

    # Prep ForeignResource and ensure does not validate security settings
    foreign_res = ForeignResource(url_string)

    # Check if already downloaded. If not, queue up download.
    if not foreign_res.cache_exists():
        await singletons.resolver_graph.download(foreign_res.url)
    return foreign_res

def apply_command_list_template(command_list, in_path, out_path, args):
    '''
    Perform necessary substitutions on a command list to create a CLI-ready
    list to launch a conversion or download process via system binary.
    '''
    replacements = {
        '$IN': in_path,
        '$OUT': out_path,
    }

    # Add in positional arguments ($0, $1, etc)
    for i, arg in enumerate(args):
        replacements['$' + str(i)] = arg

    results = [replacements.get(arg, arg) for arg in command_list]

    # Returns list of truthy replaced arguments in command
    return [item for item in results if item]


async def convert_local(path, to_type):
    '''
    Given an absolute path to a local file, convert to a given to_type
    '''
    # Now find path between types
    typed_foreign_res = TypedLocalResource(path)
    original_ts = typed_foreign_res.typestring
    conversion_path = singletons.converter_graph.find_path(
        original_ts, to_type)
    # print('Conversion path: ', conversion_path)

    # Loop through each step in graph path and convert
    for is_first, is_last, path_step in first_last_iterator(conversion_path):
        converter_class, from_ts, to_ts = path_step
        converter = converter_class()
        in_resource = TypedLocalResource(path, from_ts)
        if is_first:  # Ensure first resource is just the source one
            in_resource = typed_foreign_res
        out_resource = TypedLocalResource(path, to_ts)

        if is_last:
            out_resource = TypedPathedLocalResource(path, to_ts)
        await converter.convert(in_resource, out_resource)


def enqueue_conversion_path(url_string, to_type, enqueue_convert, custom_profiles=None):
    '''
    Given a URL string that has already been downloaded, enqueue
    necessary conversion to get to target type
    '''
    target_ts = TypeString(to_type)
    foreign_res = ForeignResource(url_string)

    # Determine the file type of the foreign resource
    typed_foreign_res = foreign_res.guess_typed()

    if not typed_foreign_res.cache_exists():
        # Symlink to new location that includes typed extension
        typed_foreign_res.symlink_from(foreign_res)

    # Now find path between types
    original_ts = typed_foreign_res.typestring
    cgraph = singletons.converter_graph
    if custom_profiles:
        path = cgraph.find_path_with_profiles(
            custom_profiles, original_ts, target_ts)
    else:
        path = cgraph.find_path(original_ts, target_ts)

    # Loop through each step in graph path and convert
    is_first = True
    for converter_class, from_ts, to_ts in path:
        converter = converter_class()
        in_resource = TypedResource(url_string, from_ts)
        if is_first:  # Ensure first resource is just the source one
            in_resource = TypedForeignResource(url_string, from_ts)
        out_resource = TypedResource(url_string, to_ts)
        enqueue_convert(converter, in_resource, out_resource)
        is_first = False
