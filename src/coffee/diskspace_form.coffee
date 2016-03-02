((window, $, templates) ->

  diskFormContainer = $ '#dashboard-diskspace-panel'
  section = diskFormContainer.parents '.o-collapsible-section'
  diskForm = diskFormContainer.find 'form'
  url = diskForm.attr 'action'
  stateUrl = diskForm.data 'state-url'
  errorMessage = templates.diskspaceConsolidateSubmitError
  uuidField = null

  NOT_STARTED = 0
  IN_PROGRESS = 1
  FINISHED = 2

  # statePoller is a FSM which polls the consolidate task state and updates the
  # UI accordingly
  statePoller =
    buttonId: null
    timer: null
    buttton: null

    getButton: () ->
      @button ?= diskFormContainer.find "##{@buttonId}"

    toggleButton: (toggle) ->
      button = @getButton()
      button.toggleClass 'diskspace-consolidation-started', not toggle
      button.prop 'disabled', not toggle
      return

    setIcon: (iconName) ->
      button = @getButton()
      (button.find '.icon').remove()
      button.prepend "<span class=\"icon icon-#{iconName}\"></span>"
      return

    update: (state) ->
      if state != 'NOT_FOUND'
        return
      # We are finished
      @stopPolling()
      @setIcon 'ok'
      setTimeout () =>
        @cleanup()
      , 7000

    cleanup: () ->
      @toggleButton yes
      @setIcon 'folder-right'

    stopPolling: () ->
      clearTimeout @timer

    start: (@buttonId) ->
      @toggleButton no
      @setIcon 'spinning-loader'
      setTimeout () =>
        @startPolling()
      , 2000

    startPolling: () ->
      poller = this
      @timer = setInterval () ->
        res = $.getJSON stateUrl
        res.done (data) ->
          console.log data, poller.currentState
          poller.update.call poller, data.state
      , 2000


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
      if (diskFormContainer.find '.o-form-errors').length
        return
      statePoller.start uuidField.val()
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
