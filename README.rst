Overview
========

This is a file content for plone which provides some useful functions, such as:

- Write downloader-name in history (ftw.journal)
- Image preview
- New FileField (stores more information in the RESPONSE header)


Install
=======

- Add ``ftw.file`` to your buildout configuration

::

    [instance]
    eggs =
        ftw.file

- Run buildout

- Install ``ftw.file`` in portal_setup

Use `ftw.file` in TinyMCE
-------------------------
- Make sure `File` is addable on the Type you use TinyMCE.

::

    <object name="Meeting Item">
        <property name="allowed_content_types">
            <element value="File" />
        </property>
    </object>

- Configure TinyMCE to create `ftw.file` Files with uploaded images. `tinymce.xml`:

::

    <object>
     <resourcetypes>
      <imageobjects purge="True">
        <element value="File"/>
      </imageobjects>
     </resourcetypes>
    </object>

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
