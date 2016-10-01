import re
from setuptools import setup


def version():
    with open('migrate/__init__.py', 'r') as version_file:
        file_content = version_file.read()
    pattern = r"""^__version__\s*=\s*['"]([^'"]*)['"]"""
    return re.search(pattern, file_content, re.M).group(1)


with open('README.rst', 'r') as readme_file:
    readme = readme_file.read()

setup(
    name='migrations',
    version=version(),
    description='Yet another Python migration tool',
    long_description=readme,
    url='https://github.com/and800/migrations',
    author='Andriy Maletsky',
    author_email='andriy.maletsky@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Version Control',
    ],
    keywords='migration',
    packages=['migrate'],
    entry_points=dict(
        console_scripts=['migrate = migrate.cli:entrypoint'],
    ),
)
