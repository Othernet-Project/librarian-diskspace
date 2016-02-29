((window, $) ->
  diskForm = $ '.consolidate-form'
  url = diskForm.attr 'action'


  submitData = (t, data) ->
    uuid = data.consolidate
    res = $.post url, data
    res.done (data) ->
      resData = $.parseJSON res.responseText
      if resData.error
        message = resData.error
      else
        message = resData.success
      t.html "<p class='consolidate o-form-error'>" + message + "</p>"

    res.fail () ->
      message = "Critical failure, see librarian log for the traceback"
      t.html "<p class='consolidate o-form-error'>" + message + "</p>"


  diskForm.on 'submit', (e) ->
    t = $ this
    e.preventDefault()
    uuid = t.attr 'id'
    data = t.serialize()
    submitData t, {'consolidate': uuid}


) this, this.jQuery
