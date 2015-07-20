import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, '../README.md')).read()
CHANGES = open(os.path.join(here, '../CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_mako',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress'
]

setup(name='peoplefinder',
      version='0.0',
      description='OpenBSC-based web application to locate people',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python, Javascript",
          "Framework :: Pyramid, Leaflet",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='NextGIS',
      author_email='info@nextgis.ru',
      url='https://github.com/nextgis/peoplefinder',
      keywords='NextGIS web wsgi pylons pyramid widgets Web dojo leaflet',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = peoplefinder:main
      """,
      )