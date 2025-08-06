# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['fede']
install_requires = \
['colorama>=0.4.6,<0.5.0']

setup_kwargs = {
    'name': 'fede',
    'version': '0.0.3',
    'description': 'My CV',
    'long_description': 'None',
    'author': 'Fede Calendino',
    'author_email': 'fede@calendino.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/fedecalendino',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
