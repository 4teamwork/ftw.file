from setuptools import setup, find_packages
import os

version = '1.16.2'

tests_require = [
    'ftw.activity',
    'ftw.builder',
    'ftw.testbrowser >= 1.22',
    'ftw.testing',
    'plone.app.testing',
    'plone.mocktestcase',
    'pyquery',
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
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

      keywords='plone file contenttype',
      author='4teamwork AG',
      author_email='mailto:info@4teamwork.ch',
      url='https://github.com/4teamwork/ftw.file',
      license='GPL2',

      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ftw'],
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'Plone',
        'setuptools',
        'ftw.journal',
        'plone.app.registry',
        'ftw.upgrade>=1.14.3',
        'ftw.calendarwidget',
        'ftw.profilehook',
        'Pillow',
        'ftw.colorbox',
        'plone.api',
        'plone.batching'
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
