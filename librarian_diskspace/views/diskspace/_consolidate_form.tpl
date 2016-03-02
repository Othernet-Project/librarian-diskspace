<%namespace name="ui" file="/ui/widgets.tpl"/>
<%namespace name="forms" file="/ui/forms.tpl"/>

<%def name="button(disk_uuid)">
    <p class="diskspace-consolidate">
        <button id="${disk_uuid}" type="submit"${' class="error"' if error and disk_uuid == action_uuid else ''} name="uuid" value="${disk_uuid}">
            <span class="icon icon-folder-right"></span>
            ## Translators, this is used as a button to move all data to that drive
            <span>${_('Move files here')}</span>
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

% if state in ['QUEUED', 'PROCESSING']:
    ${forms.form_message(_('There are move opertations in progress.'))}
% endif

% if message:
    ${forms.form_message(message)}
% endif

% if error:
    ${forms.form_errors([error])}
% endif

<form action="${i18n_url('diskspace:consolidate')}" method="POST" data-state-url="${i18n_url('diskspace:consolidate_state')}">
    % for storage in found_storages:
        <div class="diskspace-storageinfo">
            ${self.storage_info(storage)}
            <span class="storage-detail">
                ${self.button(storage.uuid)}
            </span>
        </div>
    % endfor
</form>

<script type="text/templates" id="diskspaceConsolidateSubmitError">
    ${forms.form_errors([_('Operation could not be started due to server error.')])}
</script>
