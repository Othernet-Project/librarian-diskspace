<%namespace name="ui" file="/ui/widgets.tpl"/>
<%namespace name="consolidate_button" file="_consolidate_button.tpl"/>

<def name="button(storage)">
    <form action="${i18n_url('disk:consolidate')}" method="POST"
     class="consolidate-form" id="${storage.uuid}">
      <button type="submit" name="consolidate" value="${storage.uuid}" 
      class="consolidate">Move files here</button>
    % if errors:
        % if storage.uuid in errors:
            <span>error found!</span>
        % endif
    % endif
    </form>
</def>

% for storage in found_storages:
<div class="diskspace-storageinfo">
    <%
        is_loop = storage.name.startswith('loop')
        usage = storage.stat
        disk = storage.disk

        if is_loop:
            disk_type = 'internal'
            # Translators, used as description of storage device
            disk_type_label = _('internal storage')
        elif disk.bus != 'usb':
            # This is not an attached disk
            disk_type = 'internal'
            # Translators, used as description of storage device
            disk_type_label = _('internal storage')
        elif disk.is_removable:
            # This is an USB stick
            disk_type = 'usbstick'
            # Translators, used as description of storage device
            disk_type_label = _('removable storage')
        else:
            # Most likely USB-attached hard drive
            disk_type = 'usbdrive'
            # Translators, used as description of storage device
            disk_type_label = _('removable storage')

        if is_loop:
            # Translators, appears as device name under storage devices
            disk_name = _('Virtual disk')
        elif disk.vendor or disk.model:
            disk_name = '{} {}'.format(
                disk.vendor or '',
                disk.model or '')
        else:
            disk_name = storage.name
    %>
    <span class="storage-icon icon icon-storage-${disk_type}"></span>
    <span class="storage-name storage-detail">
        ${disk_name}
    </span>
    <span class="storage-type storage-detail">
        ${disk_type_label}
    </span>
    <span class="storage-usage storage-detail">
        ${ui.progress_mini(usage.pct_used)}
        ## Translators, this is used next to disk space usage indicator in settings 
        ## panel. The {used}, {total}, and {free} are placeholders.
        ${_('{used} of {total} ({free} free)').format(
            used=h.hsize(usage.used),
            total=h.hsize(usage.total),
            free=h.hsize(usage.free))}
        ${button(storage)}
    </span>
</div>
% endfor
