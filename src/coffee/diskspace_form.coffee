((window, $, templates) ->

  diskFormContainer = $ '#dashboard-diskspace-panel'
  section = diskFormContainer.parents '.o-collapsible-section'
  diskForm = diskFormContainer.find 'form'
  url = diskForm.attr 'action'
  errorMessage = templates.diskspaceConsolidateSubmitError
  uuidField = null


  addUuidField = () ->
    # AJAX submission cannot submit different values based on what submit
    # button is clicked. We would work around this by submitting to an iframe,
    # but that doesn't sounds so good. Instead, we will add a hidden field that
    # will hold the value we want to submit.
    field = $ '<input type="hidden" name="uuid">'
    diskForm.append field
    return field


  submitData = (e) ->
    e.preventDefault()
    res = $.post url, diskForm.serialize()
    res.done (data) ->
      diskFormContainer.html data
      return
    res.fail () ->
      diskFormContainer.prepend errorMessage
      return
    res.always () ->
      section.trigger 'remax'
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


) this, this.jQuery, this.templates
