from setuptools import setup

setup(
    name='rest-serializers',
    version='0.0.2',
    description='Additional serializers for django rest framework',
    long_description=open('README.rst').read(),
    author='Stuart George',
    author_email='stuart@accentdesign.com',
    url='https://github.com/AccentDesign/Accent_RestSerializers',
    download_url='https://github.com/AccentDesign/Accent_RestSerializers/releases/tag/0.0.2',
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
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
