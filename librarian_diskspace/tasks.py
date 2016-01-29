from . import storage


def check_diskspace(supervisor):
    config = supervisor.config
    threshold = int(config['diskspace.threshold'])
    db = supervisor.exts.databases['notifications']
    supervisor.exts.notifications.delete_by_category('diskspace', db)
    if all([int(strg.stat.free) < threshold
            for strg in storage.get_content_storages(config=config)]):
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
