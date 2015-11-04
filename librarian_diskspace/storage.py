"""
zipballs.py: Tools for dealing with zipballs and their sizes

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

import pyudev
import hwd.udev
import hwd.storage
from bottle import request

from librarian_content.library.content import get_content_size


def iterpath(path):
    """
    Start from path, and iterate over the tree bottom-up until root is reached.
    Last item returned is always the root.
    """
    path = os.path.abspath(path)
    while True:
        yield path
        path = os.path.dirname(path)
    yield path


def find_mount_point(path):
    """
    Return a ``hwd.storage.MtabEntry`` object representing the mount point
    under which the path exists including the path itself if path is the mount
    point.

    For example, if path is /foo/bar and a storage device is mounted under
    /foo/bar, then ``MtabEntry`` for /foo/bar is returned. If a storage device
    is mounted under /foo, then ``MtabEntry`` for /foo is returned, and so on.

    Raises ``ValueError`` if no mount points are found.
    """
    mount_points = {e.mdir: e for e in hwd.storage.mounts()}
    for p in iterpath(path):
        if p in mount_points:
            return mount_points[p]
    raise ValueError('No mount points found in {}'.format(path))


def get_storage_by_mtab_devname(path, devname):
    """
    Return a single storage device object for which one of the aliases matches
    device name in mtab. Returns ``None`` if no devices match.
    """
    ctx = pyudev.Context()
    devs = [storage.Partition(d)
            for d in ctx.list_devices(subsystem='block', DEVTYPE='partition'))]
    for d in devs:
        if devname in d.aliases:
            return d
    return None


def get_contentdir_storage(contentdir):
    """
    Return a mountable device object matching a storage device used to house
    the content directory.
    """
    mtab_entry = find_mount_point(contendir)
    return get_storage_by_mtab_devname(mtab_entry.dev)


def free_space(config=None):
    """ Returns free space information about content directory

    :returns:   two-tuple of free space and total space
    """
    config = config or request.app.config
    cdir = config['library.contentdir']
    cdev, cfree, ctot = path_space(cdir)
    return cfree, ctot


def used_space():
    """ Return count of and total space taken by content items

    :returns:   two-tuple of content count and space used by them
    """

    db = request.db.content
    q = db.Select(['COUNT(*) AS count', 'SUM(size) AS total'],
                  sets='content')
    db.query(q)
    res = db.results
    return res[0]['count'], res[0]['total'] or 0


def needed_space(free_space, config=None):
    """ Returns the amount of space that needs to be freed, given free space

    :param free_space:  amount of currently available free space (bytes)
    :returns:           amount of additional space that should be freed (bytes)

    """
    config = config or request.app.config
    return max([0, config['storage.minfree'] - free_space])


def get_old_content(db=None):
    """ Return content ordered from oldest to newest

    :returns:   list of content ordered from oldest to newest
    """
    db = db or request.db.content
    db.query("""
             SELECT path, updated, title, views, tags, archive
             FROM content
             ORDER BY tags IS NULL DESC,
                      views ASC,
                      updated ASC,
                      archive LIKE 'ephem%' DESC;
             """)
    for item in db.results:
        yield dict((key, item[key]) for key in item.keys())


def cleanup_list(free_space, db=None, config=None):
    """ Return a generator of zipball metadata necessary to free enough space

    The generator will stop yielding as soon as enough zipballs have been
    yielded to satisfy the minimum free space requirement set in the
    configuration.
    """
    # TODO: tests
    items = get_old_content(db=db)
    config = config or request.app.config
    contentdir = config['library.contentdir']
    space = needed_space(free_space, config=config)
    while space > 0:
        content_item = next(items)
        if 'size' not in content_item:
            content_item['size'] = get_content_size(contentdir,
                                                    content_item['path'])
        space -= content_item['size']
        yield content_item
