import os

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
    Symlink all files recursively from source_d, ignoring errors (e.g. existing
    files)
    '''
    for source, destination in directory_walk(source_d, destination_d):
        try:
            os.makedirs(os.path.dirname(destination))
        except OSError:
            pass
        try:
            os.symlink(source, destination)
        except OSError:
            pass

