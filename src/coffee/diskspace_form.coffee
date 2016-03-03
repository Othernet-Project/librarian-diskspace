((window, $, templates) ->

  diskFormContainer = $ '#dashboard-diskspace-panel'
  section = diskFormContainer.parents '.o-collapsible-section'
  diskForm = diskFormContainer.find 'form'
  url = diskForm.attr 'action'
  stateUrl = diskForm.data 'state-url'
  currentUuid = diskForm.data 'started'
  errorMessage = templates.diskspaceConsolidateSubmitError
  uuidField = null


  addUuidField = () ->
    # AJAX submission cannot submit different values based on what submit
    # button is clicked. We would work around this by submitting to an iframe,
    # but that doesn't sounds so good. Instead, we will add a hidden field that
    # will hold the value we want to submit.
    field = $ '<input type="hidden" name="uuid">'
    (diskFormContainer.find 'form').append field
    return field


  updateForm = (markup) ->
    diskFormContainer.html markup
    diskForm = diskFormContainer.find 'form'
    uuidField = addUuidField()
    section.trigger 'remax'
    return


  reloadForm = () ->
    res = $.get url
    res.done updateForm


  setIcon = (button, name) ->
    (button.find '.icon').remove()
    button.prepend "<span class=\"icon icon-#{name}\"></span>"


  markDone = (uuid) ->
    button = diskFormContainer.find '#' + uuid
    setIcon button, 'ok'
    button.addClass 'diskspace-consolidation-started'
    setTimeout () ->
      button.removeClass 'diskspace-consolidation-started'
      setIcon button, 'folder-right'
    , 6000


  pollState = (uuid) ->
    setTimeout () ->
      res = $.get stateUrl
      res.done (data) ->
        if data.state?
          reloadForm()
          pollState uuid
          return
        console.log 'done'
        markDone uuid
        return
    , 2000


  submitData = (e) ->
    e.preventDefault()
    res = $.post url, diskForm.serialize()
    uuid = uuidField.val()
    res.done (data) ->
      updateForm data
      if (diskFormContainer.find '.o-form-errors').length
        return
      pollState uuid
      return
    res.fail () ->
      diskFormContainer.prepend errorMessage
      return
    return


  handleButton = (e) ->
    el = $ e.target
    uuid = el.attr 'value'
    uuidField.val uuid
    return

  uuidField = addUuidField()
  diskFormContainer.on 'click', 'button', handleButton
  diskFormContainer.on 'submit', 'form', submitData

  if currentUuid
    # Cick off the spinner immediately
    pollState currentUuid


) this, this.jQuery, this.templates
