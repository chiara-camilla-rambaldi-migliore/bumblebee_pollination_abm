from setuptools import setup

setup(name='bumblebee_pollination_abm',
      version='0.4',
      description='An ABM written with mesa, simulating the pollination behavior of bumblebees in a urban green area',
      url='https://github.com/chiara-camilla-rambaldi-migliore/bumblebee_pollination_abm',
      author='Chiara Camilla Rambaldi Migliore',
      author_email='cc.rambaldimigliore@studenti.unitn.it',
      license='MIT',
      packages=['bumblebee_pollination_abm', 'bumblebee_pollination_abm/CustomAgents'],
      install_requires=[
          'Mesa>=1.1.1,<1.2.0',
          'numpy>=1.24.1,<1.25.0',
      ],
      zip_safe=False)