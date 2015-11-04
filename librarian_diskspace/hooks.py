from .dashboard_plugin import DiskspaceDashboardPlugin


def initialize(supervisor):
    supervisor.exts.dashboard.register(DiskspaceDashboardPlugin)
