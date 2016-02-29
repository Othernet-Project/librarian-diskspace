## Translators, this is used as a button to move all data to that drive
<form action="${i18n_url('disk:consolidate')}" method="POST"
 class="consolidate-form" id="${storage.uuid}">
  <button type="submit" name="consolidate" value="${storage.uuid}" 
  class="consolidate">Move files here</button>
</form>
% if errors:
    % if storage.uuid in errors:
        <span>error found!</span>
    % endif
% endif
