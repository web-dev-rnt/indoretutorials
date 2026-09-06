import re
from datetime import date

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import LiveClassCourse, LiveClassSession
from .utils.jitsi_free import generate_room_name


@override_settings(
    JITSI_DOMAIN='meet.jit.si',
    STORAGES={
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'
        },
    },
)
class JitsiIntegrationTests(TestCase):
    def setUp(self):
        course = LiveClassCourse.objects.create(
            name='Jitsi Test Course',
            language='English',
            original_price=100,
            current_price=50,
            start_date=date.today(),
            end_date=date.today(),
        )
        self.session = LiveClassSession.objects.create(
            course=course,
            class_name='Shared Session',
            scheduled_datetime=timezone.now(),
        )

    def test_room_name_is_stable_for_the_same_session(self):
        first = generate_room_name(self.session.pk, self.session.class_name)
        second = generate_room_name(self.session.pk, self.session.class_name)
        self.assertEqual(first, second)

    def test_join_page_uses_official_api_and_same_room_on_refresh(self):
        url = reverse('live_class_join', args=[self.session.pk])
        first = self.client.get(url, secure=True)
        second = self.client.get(url, secure=True)

        self.assertEqual(first.status_code, 200)
        self.assertContains(first, 'https://meet.jit.si/external_api.js')
        first_room = re.search(rb'roomName: "([^"]+)"', first.content).group(1)
        second_room = re.search(rb'roomName: "([^"]+)"', second.content).group(1)
        self.assertEqual(first_room, second_room)
