from unittest import TestCase
try:
    from urllib.error import URLError
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
    from urllib2 import URLError
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock

from django.forms import ValidationError
from payments import RedirectNeeded, PaymentError

from . import WireProvider


VARIANT = 'Wire-3ds'


class Payment(object):

    id = 1
    variant = VARIANT
    currency = 'USD'
    total = 100
    status = 'waiting'
    fraud_status = ''

    def get_process_url(self):
        return 'http://example.com'

    def get_failure_url(self):
        return 'http://cancel.com'

    def get_success_url(self):
        return 'http://success.com'

    def change_status(self, new_status):
        self.status = new_status

    def change_fraud_status(self, fraud_status):
        self.fraud_status = fraud_status


class TestWire3DSProvider(TestCase):

    def setUp(self):
        self.payment = Payment()

    def test_process_data_supports_verification_result(self):
        provider = WireProvider()
        verification_status = 'confirmed'
        request = MagicMock()
        request.GET = {'verification_result': verification_status}
        response = provider.process_data(self.payment, request)
        self.assertEqual(self.payment.status, verification_status)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], self.payment.get_success_url())

    def test_process_data_redirects_to_success_on_payment_success(self):
        self.payment.status = 'preauth'
        provider = WireProvider()
        request = MagicMock()
        request.GET = {}
        response = provider.process_data(self.payment, request)
        self.assertEqual(response['location'], self.payment.get_success_url())

    def test_process_data_redirects_to_failure_on_payment_failure(self):
        self.payment.status = 'reject'
        provider = WireProvider()
        request = MagicMock()
        request.GET = {}
        response = provider.process_data(self.payment, request)
        self.assertEqual(response['location'], self.payment.get_failure_url())

    def test_provider_supports_non_3ds_transactions(self):
        provider = WireProvider()
        data = {
            'status': 'preauth',
            'fraud_status': 'unknown',
            'gateway_response': '3ds-disabled',
            'verification_result': ''
        }
        with self.assertRaises(RedirectNeeded) as exc:
            provider.get_form(self.payment, data)
            self.assertEqual(exc.args[0], self.payment.get_success_url())

    def test_provider_raises_verification_result_needed_on_success(self):
        provider = WireProvider()
        data = {
            'status': 'waiting',
            'fraud_status': 'unknown',
            'gateway_response': '3ds-redirect'}

        form = provider.get_form(self.payment, data)
        self.assertFalse(form.is_valid())

    def test_provider_supports_3ds_redirect(self):
        provider = WireProvider()
        verification_result = 'confirmed'
        data = {
            'status': 'waiting',
            'fraud_status': 'unknown',
            'gateway_response': '3ds-redirect',
            'verification_result': verification_result
        }
        params = urlencode({'verification_result': verification_result})
        expected_redirect = '%s?%s' % (self.payment.get_process_url(), params)

        with self.assertRaises(RedirectNeeded) as exc:
            provider.get_form(self.payment, data)
            self.assertEqual(exc.args[0], expected_redirect)

    def test_provider_supports_gateway_failure(self):
        provider = WireProvider()
        data = {
            'status': 'waiting',
            'fraud_status': 'unknown',
            'gateway_response': 'failure',
            'verification_result': ''
        }
        with self.assertRaises(URLError):
            provider.get_form(self.payment, data)

    def test_provider_raises_redirect_needed_on_success(self):
        provider = WireProvider()
        data = {
            'status': 'preauth',
            'fraud_status': 'unknown',
            'gateway_response': '3ds-disabled',
            'verification_result': ''
        }
        with self.assertRaises(RedirectNeeded) as exc:
            provider.get_form(self.payment, data)
            self.assertEqual(exc.args[0], self.payment.get_success_url())

    def test_provider_raises_redirect_needed_on_failure(self):
        provider = WireProvider()
        data = {
            'status': 'error',
            'fraud_status': 'unknown',
            'gateway_response': '3ds-disabled',
            'verification_result': ''
        }
        with self.assertRaises(RedirectNeeded) as exc:
            provider.get_form(self.payment, data)
            self.assertEqual(exc.args[0], self.payment.get_failure_url())

    def test_provider_raises_payment_error(self):
        provider = WireProvider()
        data = {
            'status': 'preauth',
            'fraud_status': 'unknown',
            'gateway_response': 'payment-error',
            'verification_result': ''
        }
        with self.assertRaises(PaymentError):
            provider.get_form(self.payment, data)

    def test_provider_switches_payment_status_on_get_form(self):
        provider = WireProvider()
        form = provider.get_form(self.payment, data={})
        self.assertEqual(self.payment.status, 'input')
