from .storage import get_content_storages
from librarian_core.contrib.templates.renderer import view, template

from bottle import request
from bottle_utils.i18n import i18n_url

_ = lambda x: x


def success_notification(supervisor, db, paths, dest):
    supervisor.exts.notifications.send(
        # Translators, notification is displayed while files are being moved to
        # external storage
        _('Files were successfully moved to {} completed successfully.'.format(
            dest)),
        category='consolidate_storage',
        dismissable=True,
        group='superuser',
        db=db)


def notification(supervisor, db, message):
    supervisor.exts.notifications.send(
        # Translators, notification is displayed while files are being moved to
        # external storage
        _(message),
        category='consolidate_storage',
        dismissable=True,
        group='superuser',
        db=db)


def consolidate(supervisor, paths, dest):
    db = supervisor.exts.databases.notifications
    success, message = supervisor.exts.fsal.consolidate(paths, dest)
    supervisor.exts.notifications.delete_by_category('consolidate_storage', db)
    if success:
        success_notification(supervisor, db, paths, dest)
    else:
        notification(supervisor, db, message)


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
    if total_size > free_space:
        return {
            'error': "Not enough free space. {} was free, needed {}".format(
                free_space, total_size)
        }

    supervisor.exts.tasks.schedule(consolidate,
                                   args=(supervisor, paths, dest),
                                   delay=0,
                                   periodic=False)

    return template('ui/feedback',
                    status='success',
                    page_title="File consolidation scheduled",
                    message="Consolidation from {} to {} has been scheduled "
                    "successfully.".format(paths, dest),
                    redirect_url=i18n_url('dashboard:main'),
                    redirect_target=_("Dashboard"))

def routes(app):
    return (
        ('disk:consolidate', schedule_consolidate,
         'POST', '/consolidate/dashboard/', {}),
    )
