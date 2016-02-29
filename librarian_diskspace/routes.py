from .storage import get_content_storages
from librarian_core.contrib.templates.renderer import view, template

from bottle import request
from bottle_utils.ajax import roca_view


_ = lambda x: x


def start_notification(supervisor, db):
    supervisor.exts.notifications.delete_by_category('consolidate_storage', db)
    supervisor.exts.notifications.send(
        # Translators, notification is displayed while files are being moved to
        # external storage
        _('Disk consolidation in progress.'),
        category='consolidate_storage',
        dismissable=False,
        priority=supervisor.exts.notifications.CRITICAL,
        group='guest',
        db=db)
    supervisor.exts.notifications.send(
        # Translators, notification is displayed while files are being moved to
        # external storage
        _('Disk consolidation in progress.'),
        category='consolidate_storage',
        dismissable=False,
        priority=supervisor.exts.notifications.CRITICAL,
        group='superuser',
        db=db)


def success_notification(supervisor, db, paths, dest):
    supervisor.exts.notifications.send(
        # Translators, notification is displayed while files are being moved to
        # external storage
        _('Disk consolidation completed successfully.'),
        category='consolidate_storage',
        dismissable=True,
        group='guest',
        db=db)
    supervisor.exts.notifications.send(
        # Translators, notification is displayed while files are being moved to
        # external storage
        _('Disk consolidation from {} to {} completed '
          'successfully.'.format(paths, dest)),
        category='consolidate_storage',
        dismissable=True,
        group='superuser',
        db=db)


def consolidate(supervisor, paths, dest):
    db = supervisor.exts.databases.notifications
    response = supervisor.exts.fsal.consolidate(paths, dest)
    import ipdb; ipdb.set_trace()

    supervisor.exts.notifications.delete_by_category('consolidate_storage', db)
    success_notification(supervisor, db, paths, dest)


#@view('dashboard/diskspace')
@roca_view('diskspace/dashboard', 'diskspace/_consolidate_button.tpl', template_func=template)
def schedule_consolidate():
    """ Gets a UUID from request context, gathers a list of all drives and
    moves content from all other drives to the drive with matching UUID """
    supervisor = request.app.supervisor

    storages = get_content_storages(supervisor)
    dest_uuid = request.params.consolidate
    dest_drive = (s for s in storages if dest_uuid == s.uuid).next()
    storages.pop(storages.index(dest_drive))
    paths = [s.base_path for s in storages]
    dest = dest_drive.base_path

    free_space = dest_drive.stat.free
    total_size = 0
    for p in paths:
        total_size += supervisor.exts.fsal.get_path_size(p)
    if total_size < free_space:
        #return error text
        return {'found_storages': storages,
            'error': "Not enough free space. {} was free, needed {}".format(
            free_space, total_size)}
    return {'found_storages': storages,
            'errors': {dest_uuid: "test error from {}".format(dest_uuid)}}

    import ipdb; ipdb.set_trace()
    consolidate(supervisor, paths, dest)
    return {'found_storages': storages,
            'errors': {
                dest_uuid: "operation completed successfully from {} to {}".format(
        paths, dest)}}

    #supervisor.exts.tasks.schedule(consolidate,
                                   #args=(supervisor, paths, dest),
                                   #delay=0,
                                   #periodic=False)



def routes(app):
    return (
            ('disk:consolidate', schedule_consolidate, 'POST', '/dashboard/consolidate/', {}),
           )
