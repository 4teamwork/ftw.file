Overview
========

This is a file content for plone which provides some useful functions, such as:

- Write downloader-name in history (ftw.journal)
- Image preview
- New FileField (sets more information in the RESPONSE header)
- Resumable downloads


Compatibility
=============

``ftw.file`` is compatible with Plone 4.3.x.

Use 1.x for Archetypes implementation of ``ftw.file`` and 2.x for Dexterity based implementation.

The ability to use ``ftw.file`` Files in TinyMCE is no longer supported for the Dexterity based
implementation (2.x).


Install
=======

- Add ``ftw.file`` to your buildout configuration

::

    [instance]
    eggs =
        ftw.file

- Run buildout

- Install ``ftw.file`` in portal_setup

- If you are using the Dexterity based implementation (2.x) then you will probably want to set `global_allow`
  for Plone's standard `File` type to False through the ZMI or a GS profile.


Links
=====

- Github: https://github.com/4teamwork/ftw.file
- Issues: https://github.com/4teamwork/ftw.file/issues
- Pypi: http://pypi.python.org/pypi/ftw.file
- Continuous integration: https://jenkins.4teamwork.ch/search?q=ftw.file


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.file`` is licensed under GNU General Public License, version 2.
