from . import storage


def check_diskspace(supervisor):
    config = supervisor.config
    contentdir = config['library.contentdir']
    threshold = int(config['diskspace.threshold'])
    db = supervisor.exts.databases['notifications']
    mtab_entry = storage.find_mount_point(contentdir)
    sdev = storage.get_storage_by_mtab_devname(mtab_entry.dev)
    free = int(sdev.stat.free)
    supervisor.exts.notifications.delete_by_category('diskspace', db)
    if free < threshold:
        supervisor.exts.notifications.send(
            'Running low on disk space, please contact an administrator.',
            category='diskspace',
            group='guest',
            db=db)
        supervisor.exts.notifications.send(
            '%sMB of free diskspace, please remove some files.' %
            str(free/1000/1000),
            category='diskspace',
            group='superuser',
            db=db)
