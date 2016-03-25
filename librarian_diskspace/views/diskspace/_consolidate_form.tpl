<%namespace name="ui" file="/ui/widgets.tpl"/>
<%namespace name="forms" file="/ui/forms.tpl"/>

<%def name="button(disk_id, current_id)">
    <% 
        is_current = current_id == disk_id
        is_active = action_id == disk_id
        cls = None
        if error and is_active:
            cls = 'error'
        elif is_current:
            cls = 'diskspace-consolidation-started'
        if is_curent:
            icon = 'spinning-loader'
            # Translators, this is used as a button to move all data to that
            # drive, while files are being moved
            label = _('Moving files here')
        else:
            icon = 'folder-right'
            # Translators, this is used as a button to move all data to that 
            # drive
            label = _('Move files here')
    %>
    <p class="diskspace-consolidate">
        <button 
            id="${disk_id}" 
            type="submit"
            name="disk_id" 
            value="${disk_id}"
            ${'disabled' if current_id else ''}
            ${'class="{}"'.format(cls) if cls else ''}>
            <span class="icon icon-${icon}"></span>
            <span>${label}</span>
        </button>
    </p>
</%def>

<%def name="storage_info(storage)">
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
    </span>
</%def>

% if message:
    ${forms.form_message(message)}
% endif

% if error:
    ${forms.form_errors([error])}
% endif

<form action="${i18n_url('diskspace:consolidate')}" method="POST" data-state-url="${i18n_url('diskspace:consolidate_state')}" data-started="${state['disk_id'] or ''}">
    % for storage in found_storages:
        <div class="diskspace-storageinfo">
            ${self.storage_info(storage)}
            <span class="storage-detail">
                ${self.button(storage.name, current_id=state)}
            </span>
        </div>
    % endfor
</form>

<script type="text/templates" id="diskspaceConsolidateSubmitError">
    ${forms.form_errors([_('Operation could not be started due to server error.')])}
</script>
