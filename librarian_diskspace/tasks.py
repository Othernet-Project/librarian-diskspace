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
            'Storage space is getting low. Please ask the administrator to take action.',
            category='diskspace',
            dismissable=False,
            group='guest',
            db=db)
        supervisor.exts.notifications.send(
            'Storage space is getting low. You will stop receiving new content if you run out of storage space. Please change or attach an external storage device.',
            category='diskspace',
            dismissable=False,
            group='superuser',
            db=db)
