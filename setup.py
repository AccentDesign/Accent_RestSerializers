from setuptools import setup
from rest_serializers import __version__

setup(
    name='rest_serializers',
    version=__version__,
    description='Additional serializers for django rest framework',
    long_description=open('README.rst').read(),
    author='Stuart George',
    author_email='stuart@accentdesign.com',
    url='https://github.com/AccentDesign/Accent_RestSerializers',
    license='MIT',
    packages=[
        'rest_serializers'
    ],
    install_requires=[
        'Django',
        'djangorestframework'
    ],
    include_package_data=True,
    keywords=['django', 'rest', 'framework', 'serializers'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
