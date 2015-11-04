from bottle import request, redirect, MultiDict, abort
from bottle_utils.html import hsize
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from librarian_content.library.archive import Archive
from librarian_core.contrib.templates.renderer import view

from . import storage


@view('diskspace/cleanup', message=None, vals=MultiDict())
def cleanup_list():
    """ Render a list of items that can be deleted """
    free = storage.get_contentdir_storage().stat.free
    return {'metadata': storage.cleanup_list(free),
            'needed': storage.needed_space(free)}


@view('diskspace/cleanup', message=None, vals=MultiDict())
def cleanup():
    forms = request.forms
    action = forms.get('action', 'check')
    if action not in ['check', 'delete']:
        # Translators, used as response to innvalid HTTP request
        abort(400, _('Invalid request'))
    free = storage.get_contentdir_storage().stat.free
    cleanup = list(storage.cleanup_list(free))
    selected = forms.getall('selection')
    metadata = list(cleanup)
    selected = [z for z in metadata if z['md5'] in selected]
    if action == 'check':
        if not selected:
            # Translators, used as message to user when clean-up is started
            # without selecting any content
            message = _('No content selected')
        else:
            tot = hsize(sum([s['size'] for s in selected]))
            message = str(
                # Translators, used when user is previewing clean-up, %s is
                # replaced by amount of content that can be freed in bytes,
                # KB, MB, etc
                _('%s can be freed by removing selected content')) % tot
        return {'vals': forms, 'metadata': metadata, 'message': message,
                'needed': storage.needed_space(free)}
    else:
        conf = request.app.config
        archive = Archive.setup(conf['library.backend'],
                                request.app.supervisor.exts.fsal,
                                request.db.content,
                                contentdir=conf['library.contentdir'],
                                meta_filenames=conf['library.metadata'])
        if selected:
            archive.remove_from_archive([z['md5'] for z in selected])
            request.app.supervisor.exts.cache.invalidate(prefix='content')
            redirect(i18n_url('content:list'))
        else:
            # Translators, error message shown on clean-up page when there was
            # no deletable content
            message = _('Nothing to delete')
        return {'vals': MultiDict(), 'metadata': cleanup,
                'message': message, 'needed': archive.needed_space()}


def routes(config):
    return (
        ('diskspace:list', cleanup_list, 'GET', '/diskspace/cleanup/', {}),
        ('diskspace:cleanup', cleanup, 'POST', '/diskspace/cleanup/', {}),
    )
