import logging

from librarian_content.library.archive import Archive

from . import zipballs


def auto_cleanup(supervisor):
    (free, _) = zipballs.free_space(config=supervisor.config)
    needed_space = zipballs.needed_space(free, config=supervisor.config)
    if not needed_space:
        return

    archive = Archive.setup(
        supervisor.config['library.backend'],
        supervisor.exts.databases.content,
        contentdir=supervisor.config['library.contentdir'],
        meta_filenames=supervisor.config['library.metadata']
    )
    deletables = zipballs.cleanup_list(free,
                                       db=supervisor.exts.databases.content,
                                       config=supervisor.config)
    relpaths = [content['path'] for content in deletables]
    deleted = archive.remove_from_archive(relpaths)
    msg = "Automatic cleanup has deleted {0} content entries.".format(deleted)
    logging.info(msg)
