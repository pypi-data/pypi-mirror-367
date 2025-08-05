from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(
  name='PythonLibTest201',
  version='0.0.1',
  author='adjutantMary',
  author_email='polshkovamamariya@gmail.com',
  description='This is the simplest module for quick work with files.',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com',
  packages=find_packages(),
  install_requires=['requests'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files speedfiles ',
  project_urls={
    'Source': 'https://github.com'
  },
  python_requires='>=3.6'
)



