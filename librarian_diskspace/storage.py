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


def iterpath(path):
    """
    Start from path, and iterate over the tree bottom-up until root is reached.
    Last item returned is always the root.
    """
    path = os.path.abspath(path)
    while path != '/':
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


def get_storage_by_mtab_devname(devname):
    """
    Return a single storage device object for which one of the aliases matches
    device name in mtab. Returns ``None`` if no devices match.
    """
    ctx = pyudev.Context()
    parts = ctx.list_devices(subsystem='block', ID_FS_USAGE='filesystem')
    ubis = ctx.list_devices(subsystem='ubi').match_attribute('alignment', '1')
    devs = map(hwd.storage.Partition, parts) + map(hwd.storage.UbiVolume, ubis)
    for d in devs:
        if devname in d.aliases:
            return d
    return None


def get_content_storages(supervisor):
    """
    Return a mountable device object matching a storage device used to house
    the content directory.
    """
    success, base_paths = supervisor.exts.fsal.list_base_paths()
    assert success, 'fsal failed to list base paths'
    storages = []
    for path in base_paths:
        mtab_entry = find_mount_point(path)
        sinfo = get_storage_by_mtab_devname(mtab_entry.dev)
        if sinfo:
            sinfo.base_path = path
            storages.append(sinfo)
    return storages
