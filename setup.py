from setuptools import setup


setup(name='bdl.engines.joyreactor',
      version='2.0.0',
      description='4Chan engine for BDL',
      url='https://www.github.com/Wawachoo/BDL_Joyreactor',
      author='Wawachoo',
      author_email='Wawachoo@users.noreply.github.com',
      license='GPLv3',
      classifiers = ['Development Status :: 3 - Alpha',
                     'Environment :: Console',
                     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                     'Natural Language :: English',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python :: 3 :: Only',
                     'Communications :: File Sharing',
                     'Topic :: Internet'],
      keywords='Joyreactor download',
      packages=['bdl.engines.joyreactor', ],
      entry_points = {'bdl.engines': ['module=bdl.engines.joyreactor']},
      install_requires=['lxml', 'requests'],
      package_data={"bdl.engines.joyreactor": ["sites.json", ]})
