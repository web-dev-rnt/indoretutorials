from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import RazorpayConfiguration


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class RazorpayConfigurationTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(
            email='admin@example.com',
            password='test-password',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(self.admin)

    def test_admin_can_save_and_view_masked_configuration(self):
        response = self.client.post(reverse('razorpay_configuration'), {
            'name': 'Test account',
            'key_id': 'rzp_test_example',
            'key_secret': 'super-secret-value',
            'is_active': 'on',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'rzp_test_example')
        self.assertContains(response, '********alue')
        self.assertNotContains(response, 'super-secret-value')
        self.assertTrue(
            RazorpayConfiguration.objects.get(name='Test account').is_active
        )

    def test_only_latest_selected_configuration_remains_active(self):
        first = RazorpayConfiguration.objects.create(
            name='First', key_id='rzp_test_first', key_secret='first-secret'
        )
        self.client.post(reverse('razorpay_configuration'), {
            'name': 'Second',
            'key_id': 'rzp_test_second',
            'key_secret': 'second-secret',
            'is_active': 'on',
        })

        first.refresh_from_db()
        self.assertFalse(first.is_active)
        self.assertTrue(RazorpayConfiguration.objects.get(name='Second').is_active)

    def test_blank_secret_on_edit_keeps_saved_secret(self):
        config = RazorpayConfiguration.objects.create(
            name='Existing', key_id='rzp_test_existing', key_secret='saved-secret'
        )
        self.client.post(reverse('razorpay_edit', args=[config.pk]), {
            'config_id': config.pk,
            'name': 'Updated',
            'key_id': 'rzp_test_updated',
            'key_secret': '',
            'is_active': 'on',
        })

        config.refresh_from_db()
        self.assertEqual(config.name, 'Updated')
        self.assertEqual(config.key_secret, 'saved-secret')

    @patch('base.views.razorpay.Client')
    def test_payment_client_uses_active_saved_configuration(self, client_class):
        RazorpayConfiguration.objects.create(
            name='Live', key_id='rzp_live_saved', key_secret='live-secret'
        )

        from base.views import get_razorpay_client

        _, key_id = get_razorpay_client()
        self.assertEqual(key_id, 'rzp_live_saved')
        client_class.assert_called_once_with(auth=('rzp_live_saved', 'live-secret'))
