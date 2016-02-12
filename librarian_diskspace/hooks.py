from bottle_utils.i18n import lazy_gettext as _

from .dashboard_plugin import DiskspaceDashboardPlugin
from .tasks import check_diskspace


def initialize(supervisor):
    supervisor.exts.dashboard.register(DiskspaceDashboardPlugin)
    supervisor.exts.settings.add_group('storage', _("Storage settings"))
    supervisor.exts.settings.add_field(name='auto_cleanup',
                                       group='storage',
                                       label=_("Automatic cleanup"),
                                       value_type=bool,
                                       required=False,
                                       default=False)


def post_start(supervisor):
    check_diskspace(supervisor)
    refresh_rate = supervisor.config['diskspace.refresh_rate']
    if not refresh_rate:
        return
    supervisor.exts.tasks.schedule(check_diskspace,
                                   args=(supervisor,),
                                   delay=refresh_rate,
                                   periodic=True)
