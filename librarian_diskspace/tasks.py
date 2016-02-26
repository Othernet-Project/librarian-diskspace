from . import storage

# FIXME: The notifications messages need to be translatable

def send_storage_notification(supervisor, db):
    supervisor.exts.notifications.send(
        'Storage space is getting low. Please ask the administrator to take '
        'action.',
        category='diskspace',
        dismissable=False,
        priority=supervisor.exts.notifications.URGENT,
        group='guest',
        db=db)
    supervisor.exts.notifications.send(
        'Storage space is getting low. You will stop receiving new content '
        'if you run out of storage space. Please change or attach an '
        'external storage device.',
        category='diskspace',
        dismissable=False,
        priority=supervisor.exts.notifications.URGENT,
        group='superuser',
        db=db)


def check_diskspace(supervisor):
    config = supervisor.config
    threshold = int(config['diskspace.threshold'])
    db = supervisor.exts.databases['notifications']
    supervisor.exts.notifications.delete_by_category('diskspace', db)
    storage_devices = storage.get_content_storages(supervisor)
    if not storage_devices:
        # None found, probably due to misconfiguration
        return
    # Note that we only check the last storage. It is assumed that the storage
    # configuration places external storage at the last position in the list.
    if int(storage_devices[-1].stat.free) < threshold:
        send_storage_notification(supervisor, db)
