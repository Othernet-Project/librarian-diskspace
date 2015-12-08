===================
librarian-diskspace
===================

A dashboard plugin which displays the available storage devices and disk space
usage on them.

Installation
------------

The component has the following dependencies:

- librarian-core_
- librarian-dashboard_
- librarian-content_
- hwd_

To enable this component, add it to the list of components in librarian_'s
`config.ini` file, e.g.::

    [app]
    +components =
        librarian_diskspace

Development
-----------

In order to recompile static assets, make sure that compass_ and coffeescript_
are installed on your system. To perform a one-time recompilation, execute::

    make recompile

To enable the filesystem watcher and perform automatic recompilation on changes,
use::

    make watch

.. _librarian: https://github.com/Outernet-Project/librarian
.. _librarian-core: https://github.com/Outernet-Project/librarian-core
.. _librarian-content: https://github.com/Outernet-Project/librarian-content
.. _librarian-dashboard: https://github.com/Outernet-Project/librarian-dashboard
.. _hwd: https://github.com/Outernet-Project/hwd
.. _compass: http://compass-style.org/
.. _coffeescript: http://coffeescript.org/
