import setuptools

with open('README.md', 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name='acestream-launcher',
  version='2.0.0',
  author='Jonian Guveli',
  author_email='jonian@hardpixel.eu',
  description='Open AceStream links with a Media Player of your choice',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/jonian/acestream-launcher',
  packages=setuptools.find_packages(),
  data_files=[
    ('share/applications', ['acestream-launcher.desktop'])
  ],
  install_requires=[
    'acestream>=0.1.3'
  ],
  classifiers=[
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Operating System :: POSIX :: Linux'
  ],
  project_urls={
    'Bug Reports': 'https://github.com/jonian/acestream-launcher/issues',
    'Source': 'https://github.com/jonian/acestream-launcher',
  },
  entry_points={
    'console_scripts': ['acestream-launcher = acestream_launcher.launcher:main']
  }
)
