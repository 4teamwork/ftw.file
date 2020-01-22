Overview
========

This is a file content for plone which provides some useful functions, such as:

- Write downloader-name in history (ftw.journal)
- Image preview
- Resumable downloads

Note: The ability to upload new file versions via drag and drop was removed in version 2.3.0
to reduce support overhead (it only worked in Plone 4).


Compatibility
=============

``ftw.file`` is compatible with Plone 4.3.x and 5.1.x.

Use 1.x for Archetypes implementation of ``ftw.file`` and 2.x for Dexterity
based implementation.

The ability to use ``ftw.file`` Files in TinyMCE is no longer supported for
the Dexterity based implementation (2.x).

Enabling versioning in 2.x
--------------------------

To enable versioning for the ftw.file.File dexterity type, you should go to
the Types control panel for this type and select either manual or automatic
versioning.  This is equivalent to the following GenericSetup configuration
in `repositorytool.xml`:

::

	<?xml version="1.0"?>
	<repositorytool>
	  <policymap purge="false">
	    <type name="ftw.file.File">
	      <policy name="at_edit_autoversion" />
	      <policy name="version_on_revert" />
	    </type>
	  </policymap>
	</repositorytool>


And, yes `at_edit_autoversion` IS the correct setting for dexterity types.


Migration from 1.x to 2.x
-------------------------

A migration step is provided for migrating from Archetypes to Dexterity
implementations.
If however, you have been using TinyMCE integration in 1.x then you will need
replace ``ftw.file.File`` with ``Image`` (or another type as you see fit) in
the setting "TinyMCE / resourcetypes / imageobjects".


Install
=======

- Add ``ftw.file`` to your buildout configuration

::

    [instance]
    eggs =
        ftw.file

- Run buildout

- Install ``ftw.file`` in portal_setup

- If you are using the Dexterity based implementation (2.x) then you will
  probably want to set `global_allow` for Plone's standard `File` type to
  False through the ZMI or a GS profile.


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
