#!/usr/bin/env python
from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')

PACKAGES = [
    'pysar_payments',
    'pysar_payments.authorizenet',
    'pysar_payments.braintree',
    'pysar_payments.cybersource',
    'pysar_payments.dummy',
    'pysar_payments.dotpay',
    'pysar_payments.paypal',
    'pysar_payments.sagepay',
    'pysar_payments.sofort',
    'pysar_payments.stripe',
    'pysar_payments.wallet',
    'pysar_payments.wire']

REQUIREMENTS = [
    'braintree>=3.14.0',
    'Django>=1.5',
    'pycrypto>=2.6',
    'PyJWT>=1.3.0',
    'requests>=1.2.0',
    'stripe>=1.9.8',
    'suds-jurko>=0.6',
    'xmltodict>=0.9.2']


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='django-pysar_payments',
    author='Mirumee Software',
    author_email='hello@mirumee.com',
    description='Universal payment handling for Django (forked)',
    version='0.7.3',
    url='https://github.com/imakin/django-payments',
    packages=PACKAGES,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=REQUIREMENTS,
    cmdclass={
        'test': PyTest},
    tests_require=[
        'mock',
        'pytest',
        'pytest-django'
    ],
    zip_safe=False)
