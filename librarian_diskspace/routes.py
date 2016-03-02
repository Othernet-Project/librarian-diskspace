import logging
import functools

from bottle import request
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import i18n_url, lazy_gettext as _
from bottle_utils.html import hsize

from librarian_core.contrib.templates.renderer import view, template

from .storage import get_content_storages

gettext = lambda x: x


# Translators, notification displayed if files were moved to
# external storage successfully
CONSOLIDATE_SUCCESS = gettext('Files were successfully moved to '
                              '{storage_name}')

# Translators, notification displayed if moving files to
# external storage failed
CONSOLIDATE_FAILURE = gettext('Files could not be moved to '
                              '{storage_name}')


def get_storage_name(storage):
    name = storage.name
    is_loop = name and name.startswith('loop')
    disk = storage.disk
    if is_loop:
        name = 'Virtual disk'
    elif disk.vendor or disk.model:
        name = '{} {}'.format(disk.vendor or '', disk.model or '')
    return name


def consolidation_notify(supervisor, db, message):
    supervisor.exts.notifications.send(
        message,
        category='consolidate_storage',
        dismissable=True,
        group='superuser',
        db=db)


def consolidate(supervisor, paths, dest, storage_name):
    logging.info('Started consolidating to %s', dest)
    db = supervisor.exts.databases.notifications
    cache = supervisor.exts.cache
    success, message = supervisor.exts.fsal.consolidate(paths, dest)
    supervisor.exts.notifications.delete_by_category('consolidate_storage', db)
    if success:
        logging.info('Consolidating to %s finished', dest)
        message = CONSOLIDATE_SUCCESS.format(storage_name=storage_name)
    else:
        logging.error('Consolidating to %s failed', dest)
        message = CONSOLIDATE_FAILURE.format(storage_name=storage_name)
    consolidation_notify(supervisor, db, message)
    cache.delete('consolidate_task_id')


def with_storages(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        storages = get_content_storages(request.app.supervisor)
        kwargs['storages'] = storages
        return fn(*args, **kwargs)
    return wrapper


@view('diskspace/consolidate.tpl')
@with_storages
def show_consolidate_form(storages):
    return dict(found_storages=storages)


@roca_view('diskspace/consolidate.tpl', 'diskspace/_consolidate_form.tpl',
           template_func=template)
@with_storages
def schedule_consolidate(storages):
    """ Gets a UUID from request context, gathers a list of all drives and
    moves content from all other drives to the drive with matching UUID """
    supervisor = request.app.supervisor
    tasks = supervisor.exts.tasks
    cache = supervisor.exts.cache
    dest_uuid = request.params.uuid

    response_ctx = {
        'found_storages': storages,
        'uuid': dest_uuid,
    }

    task_id = cache.get('consolidate_task_id')
    if task_id:
        # There is already a task running, so we can't schedule another one
        response_ctx.update({
            # Translators, error message shown when moving of files is
            # attempted while another move task is already running.
            'error': _('A scheduled move is already running. You will be '
                       'notified when it finishes. Please try again '
                       'once the current operation is finished.')})
        return response_ctx

    # Get source and detinations drives
    src_drives = []
    dest_drive = None
    for s in storages:
        print(dest_uuid, s, s.uuid)
        if s.uuid == dest_uuid:
            dest_drive = s
        else:
            src_drives.append(s)

    # Is the destination drive still there?
    if not dest_drive:
        # Translators, error message shown when destination drive is removed or
        # otherwise becomes inaccessible before files are moved to it.
        response_ctx['error'] = _('Destination drive disappeared. Please '
                                  'reattach the drive and retry.')
        return response_ctx

    dest_name = get_storage_name(dest_drive)
    dest = dest_drive.base_path
    free_space = dest_drive.stat.free
    total_size = 0
    paths = [s.base_path for s in src_drives]

    # Calculate total size of all files in all source base paths
    for p in paths:
        total_size += supervisor.exts.fsal.get_path_size(p)

    if total_size > free_space:
        # Not enough space on target drive
        response_ctx['error'] = _(
            "Not enough free space. {size} needed.").format(
                size=hsize(total_size))
        return response_ctx

    task_id = tasks.schedule(consolidate,
                             args=(supervisor, paths, dest, dest_name),
                             delay=0,
                             periodic=False)
    # Cache the task id so it can be looked up later
    cache.set('consolidate_task_id', task_id)

    return template('ui/feedback',
                    status='success',
                    page_title="File consolidation scheduled",
                    message=_(
                        'Files are now being moved to {destination}. '
                        'You will be notified when move is complete.').format(
                            destination=dest),
                    redirect_url=i18n_url('dashboard:main'),
                    redirect_target=_("Dashboard"))


def routes(app):
    return (
        ('diskspace:show_consolidate_form', show_consolidate_form,
         'GET', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate', schedule_consolidate,
         'POST', '/diskspace/consolidate/', {}),
    )
