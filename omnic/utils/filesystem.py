import os
import shutil


def directory_walk(source_d, destination_d):
    '''
    Walk a directory structure and yield full parallel source and destination
    files, munging filenames as necessary
    '''
    for dirpath, dirnames, filenames in os.walk(source_d):
        relpath = os.path.relpath(dirpath, source_d)
        if relpath == '.':
            relpath = ''  # remove implied '.'
        for filename in filenames:
            suffix = filename
            if relpath:
                suffix = os.path.join(relpath, filename)
            full_source_path = os.path.join(source_d, suffix)
            full_destination_path = os.path.join(destination_d, suffix)
            yield full_source_path, full_destination_path


def recursive_symlink_dirs(source_d, destination_d):
    '''
    Create dirs and symlink all files recursively from source_d, ignoring
    errors (e.g. existing files)
    '''
    func = os.symlink
    if os.name == 'nt':
        # NOTE: need to verify that default perms only allow admins to create
        # symlinks on Windows
        func = shutil.copy
    if os.path.exists(destination_d):
        os.rmdir(destination_d)
    shutil.copytree(source_d, destination_d, copy_function=func)


def recursive_hardlink_dirs(source_d, destination_d):
    '''
    Same as above, except creating hardlinks for all files
    '''
    func = os.link
    if os.name == 'nt':
        func = shutil.copy
    if os.path.exists(destination_d):
        os.rmdir(destination_d)
    shutil.copytree(source_d, destination_d, copy_function=func)


def _make_empty_dir_dict(path):
    return {
        'path': path,
        'type': 'directory',
        'children': [],
    }


def _make_child(info):
    return {
        'mode': info[0],
        'type': info[1],
        'sha': info[2],
        'size': int(info[3]),
        'path': info[4],
    }


PATH = 4


def flat_git_tree_to_nested(flat_tree, prefix=''):
    '''
    Given an array in format:
        [
            ["100644", "blob", "ab3ce...", "748", ".gitignore" ],
            ["100644", "blob", "ab3ce...", "748", "path/to/thing" ],
            ...
        ]

    Outputs in a nested format:
        {
            "path": "/",
            "type": "directory",
            "children": [
                {
                    "type": "blob",
                    "size": 748,
                    "sha": "ab3ce...",
                    "mode": "100644",
                },
                ...
            ],
            ...
        }
    '''
    root = _make_empty_dir_dict(prefix if prefix else '/')

    # Filter all descendents of this prefix
    descendent_files = [
        info for info in flat_tree
        if os.path.dirname(info[PATH]).startswith(prefix)
    ]

    # Figure out strictly leaf nodes of this tree (can be immediately added as
    # children)
    children_files = [
        info for info in descendent_files
        if os.path.dirname(info[PATH]) == prefix
    ]

    # Figure out all descendent directories
    descendent_dirs = set(
        os.path.dirname(info[PATH]) for info in descendent_files
        if os.path.dirname(info[PATH]).startswith(prefix)
        and not os.path.dirname(info[PATH]) == prefix
    )

    # Figure out all descendent directories
    children_dirs = set(
        dir_path for dir_path in descendent_dirs
        if os.path.dirname(dir_path) == prefix
    )

    # Recurse into children dirs, constructing file trees for each of them,
    # then appending those
    for dir_path in children_dirs:
        info = flat_git_tree_to_nested(descendent_files, prefix=dir_path)
        root['children'].append(info)

    # Append direct children files
    for info in children_files:
        root['children'].append(_make_child(info))

    return root
