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
