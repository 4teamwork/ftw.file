from setuptools import setup, find_packages
import os

version = '1.4.12'
maintainer = 'Thomas Buchberger'

tests_require = [
    'plone.app.testing',
    'plone.mocktestcase',
]

setup(name='ftw.file',
      version=version,
      description="A file content type for gov usecases",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone :: 4.1",
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone file contenttype',
      maintainer=maintainer,
      author='4teamwork GmbH',
      author_email='info@4teamwork.ch',
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
