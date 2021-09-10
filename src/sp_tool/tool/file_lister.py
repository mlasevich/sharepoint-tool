""" File Lister """
import fnmatch
import os
from typing import List

from .logging import LOG


def _matches(file, glob):
    """ check if file matches a glob"""
    return fnmatch.fnmatch(file, glob)


def _matches_one_of(file, globs):
    """ check if file one of the provided globs """
    for glob in globs:
        if fnmatch.fnmatch(file, glob):
            return True
    return False


def _filter_files(file_list, include, exclude):
    """ Filter a list of files """
    files = []
    for file in file_list:
        if not _matches_one_of(file, include):
            LOG.debug("File %s does not match any of the include patterns",
                      file)
            continue
        if _matches_one_of(file, exclude):
            LOG.debug("File %s matches an exclude pattern, ignoring", file)
            continue
        LOG.debug("Found file '%s'", file)
        files.append(file)
    return files


def list_files(directory, recurse=False,
               include: List[str] = None, exclude: List[str] = None,
               include_dirs: List[str] = None, exclude_dirs: List[str] = None):
    """ List files in directory with includes or excludes """
    # pylint: disable=too-many-arguments
    files = []
    src_dir = directory.rstrip('/')

    if not include:
        include = ['*']
    if not include_dirs:
        include_dirs = ['*']
    if not exclude:
        exclude = []
    if not exclude_dirs:
        exclude_dirs = []

    LOG.info("Scanning '%s'.Includes: %s. Excludes: %s "
             "Include Dirs: %s. Exclude Dirs: %s", src_dir,
             str(include)[1:-1], str(exclude)[1:-1],
             str(include_dirs)[1:-1], str(exclude_dirs)[1:-1]
             )

    if not os.path.isdir(src_dir):
        LOG.warning("Directory %s does not exist", src_dir)
        return files

    for root, folders, local_files in os.walk(src_dir):
        if not recurse and root != src_dir:
            continue
        root_path = root.split('/')
        excluded = False
        for path in root_path:
            if _matches_one_of(path, exclude_dirs):
                LOG.debug("Directory %s matched an exclude, skipping", root)
                excluded = True
                break
        if excluded:
            continue
        LOG.debug("Scanning '%s' - Folders: %s Files: %s", root, folders,
                  local_files)
        files += [f"{root}/{file}" for file in _filter_files(local_files,
                                                             include, exclude)]
    return files
