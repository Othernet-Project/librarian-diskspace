from .auto_cleanup import auto_cleanup
from .dashboard_plugin import DiskspaceDashboardPlugin


def initialize(supervisor):
    supervisor.exts.dashboard.register(DiskspaceDashboardPlugin)
    if supervisor.config.get('storage.auto_cleanup', False):
        auto_cleanup_every = supervisor.config['storage.auto_cleanup_every']
        supervisor.exts.tasks.schedule(auto_cleanup,
                                       args=(supervisor,),
                                       delay=auto_cleanup_every,
                                       periodic=True)
