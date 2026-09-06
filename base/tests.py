from io import BytesIO
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from base.models import User
from elibrary.models import ELibraryCourse, ELibraryDownload, ELibraryPDF
from video_courses.dropbox_storage import DropboxStorage
from video_courses.models import Category


class ManagementAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="student@example.com",
            password="strong-test-password",
        )

    def test_anonymous_users_cannot_open_management_pages(self):
        for url in (
            "/video-courses/create/",
            "/video-courses/manage/",
            "/liveclass/",
            "/liveclass/create/",
            "/banner-edit/",
        ):
            with self.subTest(url=url):
                response = self.client.get(url, secure=True)
                self.assertEqual(response.status_code, 302)

    def test_regular_users_cannot_open_management_pages(self):
        self.client.force_login(self.user)
        for url in (
            "/video-courses/create/",
            "/liveclass/",
            "/banner-edit/",
            "/smtp/",
        ):
            with self.subTest(url=url):
                response = self.client.get(url, secure=True)
                self.assertEqual(response.status_code, 302)


class ELibraryAccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="reader@example.com",
            password="strong-test-password",
        )
        category = Category.objects.create(name="Books")
        self.course = ELibraryCourse.objects.create(
            title="Paid Library",
            description="Course description",
            short_description="Short description",
            category=category,
            instructor="Instructor",
            price=100,
            created_by=self.user,
        )
        self.pdf = ELibraryPDF(
            course=self.course,
            title="Chapter One",
            file="elibrary/pdfs/chapter-one.pdf",
            uploaded_by=self.user,
        )
        ELibraryPDF.objects.bulk_create([self.pdf])
        self.client.force_login(self.user)

    def test_paid_pdf_rejects_user_without_access(self):
        response = self.client.get(
            reverse("view_pdf", args=[self.pdf.pk]),
            secure=True,
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ELibraryDownload.objects.count(), 0)

    def test_preview_pdf_streams_without_local_path(self):
        self.pdf.is_preview = True
        ELibraryPDF.objects.filter(pk=self.pdf.pk).update(is_preview=True)

        with patch.object(
            DropboxStorage,
            "open",
            return_value=BytesIO(b"%PDF-1.4 test"),
        ):
            response = self.client.get(
                reverse("view_pdf", args=[self.pdf.pk]),
                secure=True,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(ELibraryDownload.objects.count(), 1)
        self.pdf.refresh_from_db()
        self.assertEqual(self.pdf.download_count, 1)


class PerformanceAndPWATests(TestCase):
    def setUp(self):
        cache.clear()

    def test_dropbox_url_generation_does_not_make_network_request(self):
        storage = DropboxStorage()
        with self.settings(
            DROPBOX_REFRESH_TOKEN="refresh-token",
            DROPBOX_APP_KEY="app-key",
            DROPBOX_APP_SECRET="app-secret",
        ):
            with patch.object(
                DropboxStorage,
                "temporary_url",
                side_effect=AssertionError("network resolution must not happen during render"),
            ):
                url = storage.url("video_courses/example/thumb.jpg")
        self.assertTrue(url.startswith("/dropbox-file/"))

    def test_missing_dropbox_credentials_use_local_image_fallback(self):
        storage = DropboxStorage()
        with self.settings(
            DROPBOX_REFRESH_TOKEN="",
            DROPBOX_APP_KEY="",
            DROPBOX_APP_SECRET="",
            STORAGES={
                "default": {
                    "BACKEND": "django.core.files.storage.FileSystemStorage"
                },
                "staticfiles": {
                    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
                },
            },
        ):
            url = storage.url("video_courses/example/thumb.jpg")
        self.assertTrue(url.endswith("/static/img/default-thumb.jpg"))

    def test_homepage_has_no_blocking_checkout_or_external_font_stylesheet(self):
        with self.settings(
            STORAGES={
                "default": {
                    "BACKEND": "django.core.files.storage.FileSystemStorage"
                },
                "staticfiles": {
                    "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
                },
            },
        ):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "checkout.razorpay.com")
        self.assertNotContains(response, "fonts.googleapis.com")

    def test_service_worker_only_caches_public_static_files(self):
        response = self.client.get(reverse("service-worker"), secure=True)
        self.assertEqual(response.status_code, 200)
        source = response.content.decode("utf-8")
        self.assertIn("url.pathname.startsWith('/static/')", source)
        self.assertNotIn("cache.put(request, responseClone)", source)
        self.assertIn("/static/img/icon-192.png", source)

    def test_manifest_references_existing_icon_names(self):
        response = self.client.get(reverse("manifest1"), secure=True)
        self.assertEqual(response.status_code, 200)
        icon_urls = {icon["src"] for icon in response.json()["icons"]}
        self.assertTrue(any(url.endswith("/static/img/icon-192.png") for url in icon_urls))
        self.assertTrue(any(url.endswith("/static/img/icon-512.png") for url in icon_urls))
