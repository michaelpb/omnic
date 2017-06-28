
from omnic import singletons
from omnic.types.resource import (ForeignResource, TypedForeignResource,
                                  TypedLocalResource, TypedPathedLocalResource,
                                  TypedResource)
from omnic.types.typestring import TypeString
from omnic.utils.iters import first_last_iterator


async def convert_local(path, to_type):
    '''
    Given an absolute path to a local file, convert to a given to_type
    '''
    # Now find path between types
    typed_foreign_res = TypedLocalResource(path)
    original_ts = typed_foreign_res.typestring
    conversion_path = singletons.converter_graph.find_path(
        original_ts, to_type)
    print('Conversion path: ', conversion_path)

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


def enqueue_conversion_path(url_string, to_type, enqueue_convert):
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
    path = singletons.converter_graph.find_path(original_ts, target_ts)

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
