from setuptools import setup, find_packages
import os

version = '1.8.3.dev0'
maintainer = 'Thomas Buchberger'

tests_require = [
    'plone.app.testing',
    'plone.mocktestcase',
    'pyquery',
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing[splinter]',
    ]

setup(name='ftw.file',
      version=version,
      description="A file content type for gov usecases",
      long_description=open("README.rst").read() + "\n" + \
          open(os.path.join("docs", "HISTORY.txt")).read(),

      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers

      classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.2',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='plone file contenttype',
      maintainer=maintainer,
      author='4teamwork GmbH',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.file',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'setuptools',
        'ftw.journal',
        'plone.app.registry',
        'ftw.upgrade>=1.4.0',
        'ftw.calendarwidget',
        'Pillow',
        'ftw.colorbox',
        # -*- Extra requirements: -*-
        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),

      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
