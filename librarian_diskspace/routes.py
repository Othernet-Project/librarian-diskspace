from .storage import get_content_storages

from bottle import request


def consolidate():
    supervisor = request.app.supervisor
    storages = get_content_storages(supervisor)
    dest_uuid = request.params.consolidate
    dest_drive = (s for s in storages if dest_uuid == s.uuid).next()
    storages.pop(storages.index(dest_drive))
    paths = [s.base_path for s in storages]
    dest = dest_drive.base_path
    supervisor.exts.fsal.consolidate(paths, dest)
    return 'transferred all content from {} to {}'.format(
        "'%s'" % ', '.join(paths)
        , dest)


def routes(app):
    return (
            ('disk:consolidate', consolidate, 'POST', '/dashboard/consolidate/', {}),
           )
