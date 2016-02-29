((window, $) ->
  diskForm = $ '.consolidate-form'
  url = diskForm.attr 'action'


  submitData = (data) ->
    console.log(data)
    res = $.post url, data
    console.log(res)
    res.done (data) ->
      diskForm.html "success"

    res.fail () ->
      diskForm.html "failure"


  diskForm.on 'submit', (e) ->
    e.preventDefault()
    uuid = diskForm.attr 'id'
    submitData uuid


) this, this.jQuery
