from __future__ import unicode_literals
from django import forms

from ..forms import PaymentForm
from ..models import PAYMENT_STATUS_CHOICES, FRAUD_CHOICES
from django.utils.translation import ugettext_lazy as _


class WireForm(PaymentForm):

    RESPONSE_CHOICES = (
        ('3ds-disabled', '3DS disabled'),
        ('3ds-redirect', '3DS redirect'),
        ('failure', 'Gateway connection error'),
        ('payment-error', 'Gateway returned unsupported response')
    )
    status = forms.ChoiceField(choices=PAYMENT_STATUS_CHOICES)
    raup_status = forms.ChoiceField(choices=FRAUD_CHOICES)
    gateway_response = forms.ChoiceField(choices=RESPONSE_CHOICES)
    verification_result = forms.ChoiceField(choices=PAYMENT_STATUS_CHOICES,
                                            required=False)
    ammount = forms.DecimalField(
            label=_('Transfered Ammount'),
            decimal_places=2,
            max_digits=14
    )
    transfer_destination = forms.CharField(
            label=_('Transfer Destination'), 
            max_length=255
    )
    transfer_origin_name = forms.CharField(
            max_length=255,
            label=_('Bank Account Owner\'s name')
    )
    transfer_origin_number = forms.CharField(
            max_length=255,
            label=_('Bank Account Number')
    )
    keterangan_tambahan = forms.CharField(
            label=_('Additional Note'),
            required=False
    )
    additional_doc = forms.FileField(
            label=_('Document'),
            #~ upload_to='documents/confirmation/%Y',
            required=False
    )
    def clean(self):
        cleaned_data = super(WireForm, self).clean()
        gateway_response = cleaned_data.get('gateway_response')
        verification_result = cleaned_data.get('verification_result')
        if gateway_response == '3ds-redirect' and not verification_result:
            raise forms.ValidationError(
                'When 3DS is enabled you must set post validation status')
        return cleaned_data
