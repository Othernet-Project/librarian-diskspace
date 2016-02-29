## Translators, this is used as a button to move all data to that drive
<def name="button(uuid)">
    <form action="${i18n_url('disk:consolidate')}" method="POST"
     class="consolidate-form" id="${uuid}">
      <button type="submit" name="consolidate" value="${uuid}" 
      class="consolidate">Move files here</button>
    % if errors:
        % if uuid in errors:
            ${errors[uuid]}
            <span>error found!</span>
        % endif
    % endif
    </form>
</def>
