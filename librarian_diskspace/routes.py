import logging
import functools

from bottle import request
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import i18n_url, lazy_gettext as _
from bottle_utils.html import hsize

from librarian_core.contrib.templates.renderer import view, template

from .storage import get_content_storages

gettext = lambda x: x

CONSOLIDATE_KEY = 'consolidate_task_id'

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


def consolidation_notify(supervisor, db, message, priority):
    supervisor.exts.notifications.send(
        message,
        category='consolidate_storage',
        dismissable=True,
        group='superuser',
        priority=priority,
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
        priority = supervisor.exts.notifications.NORMAL
    else:
        logging.error('Consolidating to %s failed', dest)
        message = CONSOLIDATE_FAILURE.format(storage_name=storage_name)
        priority = supervisor.exts.notifications.URGENT
    consolidation_notify(supervisor, db, message, priority)
    cache.delete(CONSOLIDATE_KEY)


def with_storages(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        storages = get_content_storages(request.app.supervisor)
        kwargs['storages'] = storages
        return fn(*args, **kwargs)
    return wrapper


def consolidate_state():
    tasks = request.app.supervisor.exts.tasks
    task_id = request.app.supervisor.exts.cache.get(CONSOLIDATE_KEY)
    if not task_id:
        return dict(state=tasks.NOT_FOUND)
    return dict(state=tasks.get_status(task_id))


@view('diskspace/consolidate.tpl')
@with_storages
def show_consolidate_form(storages):
    return dict(found_storages=storages, state=consolidate_state())


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
        'state': consolidate_state(),
    }

    task_id = cache.get('consolidate_task_id')
    if task_id:
        # There is already a task running, so we can't schedule another one
        # Translators, error message shown when moving of files is
        # attempted while another move task is already running.
        response_ctx['error'] = _('A scheduled move is already running. You '
                                  'will be notified when it finishes. Please '
                                  'try again once the current operation is '
                                  'finished.')
        return response_ctx

    # Get source and detinations drives
    src_drives = []
    dest_drive = None
    for s in storages:
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

    if not src_drives:
        # Translators, error message shown when moving files to a storage
        # device where no other storage devices are present other than the
        # target device.
        response_ctx['error'] = _('There are no other drives to move files '
                                  'from.')
        return response_ctx

    dest_name = get_storage_name(dest_drive)
    dest = dest_drive.base_path
    free_space = dest_drive.stat.free
    total_size = 0
    paths = [s.base_path for s in src_drives]

    # Calculate total size of all files in all source base paths
    for p in paths:
        success, size = supervisor.exts.fsal.get_path_size(p)
        if not success:
            response_ctx['error'] = _('Could not calculate file sizes due '
                                      'to disk error. Please check your '
                                      'storage device and try again.')
            return response_ctx
        total_size += size

    if total_size <= 0:
        # Translators, error message shown when moving files to a storage
        # device, where no movable files are present.
        response_ctx['error'] = _('There are no files to be moved.')
        return response_ctx

    if not free_space or total_size > free_space:
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
    cache.set(CONSOLIDATE_KEY, task_id)

    message = _('Files are now being moved to {destination}. You will be '
                'notified when the operation is finished.').format(
                    destination=dest)

    if request.is_xhr:
        response_ctx['message'] = message
        return response_ctx

    return template('ui/feedback',
                    status='success',
                    page_title="File consolidation scheduled",
                    message=message,
                    redirect_url=i18n_url('dashboard:main'),
                    redirect_target=_("settings"))


def routes(app):
    return (
        ('diskspace:show_consolidate_form', show_consolidate_form,
         'GET', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate', schedule_consolidate,
         'POST', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate_state', consolidate_state,
         'GET', '/diskspace/consolidate/state', {})
    )
