import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'jcu.common[forms,static]',
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_deform',
    'pyramid_beaker',
    'pyramid_fanstatic',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'pytagcloud',
    'pygame',
    'simplejson',
    'bleach',
    'css.css3githubbuttons',
    'js.jquery',
    ]

setup(name='jcu.words',
      version='0.0',
      description='jcu.words',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='jcuwords',
      setup_requires=[
          'setuptools-git',
      ],
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = jcuwords:main

      [fanstatic.libraries]
      jcu.words = jcuwords.resources:library

      [console_scripts]
      initialize_jcu.words_db = jcuwords.scripts.initializedb:main
      """,
      )

