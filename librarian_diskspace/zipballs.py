"""
zipballs.py: Tools for dealing with zipballs and their sizes

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request

from librarian_content.library.content import get_content_size


def path_space(path):
    """ Return device number and free space in bytes for given path

    :param path:    path for which to return the data
    :returns:       three-tuple containing drive number, free space, total
                    space
    """
    dev = os.stat(path).st_dev
    stat = os.statvfs(path)
    free = stat.f_frsize * stat.f_bavail
    total = stat.f_blocks * stat.f_frsize
    return dev, free, total


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
