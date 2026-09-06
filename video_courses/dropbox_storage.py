import hashlib
import logging
import re

import dropbox
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.core import signing
from django.urls import reverse
from django.templatetags.static import static
from django.utils.deconstruct import deconstructible
from dropbox.files import WriteMode


logger = logging.getLogger(__name__)


@deconstructible
class DropboxStorage(Storage):
    """Dropbox-backed storage with cached temporary download URLs."""

    BASE_PATH = "/elibrary"
    CHUNK_SIZE = 4 * 1024 * 1024
    URL_CACHE_SECONDS = 3 * 60 * 60 + 45 * 60
    MISSING_URL_CACHE_SECONDS = 5 * 60
    IMAGE_EXTENSIONS = {".avif", ".gif", ".jpeg", ".jpg", ".png", ".webp"}

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Initialize the network client lazily instead of during Django import."""
        if self._client is None:
            credentials = (
                settings.DROPBOX_REFRESH_TOKEN,
                settings.DROPBOX_APP_KEY,
                settings.DROPBOX_APP_SECRET,
            )
            if not all(credentials):
                raise ImproperlyConfigured(
                    "Dropbox credentials must be configured through environment variables."
                )
            self._client = dropbox.Dropbox(
                oauth2_refresh_token=settings.DROPBOX_REFRESH_TOKEN,
                app_key=settings.DROPBOX_APP_KEY,
                app_secret=settings.DROPBOX_APP_SECRET,
            )
        return self._client

    def _clean_path(self, name):
        name = str(name).replace("\\", "/")
        name = re.sub(r"[^a-zA-Z0-9._/-]", "_", name)
        while "//" in name:
            name = name.replace("//", "/")
        return f"{self.BASE_PATH}/{name.lstrip('/')}"

    def _url_cache_key(self, path):
        digest = hashlib.sha256(path.encode("utf-8")).hexdigest()
        return f"dropbox-url:{digest}"

    def _is_configured(self):
        return all((
            settings.DROPBOX_REFRESH_TOKEN,
            settings.DROPBOX_APP_KEY,
            settings.DROPBOX_APP_SECRET,
        ))

    def _fallback_url(self, name):
        extension = f".{str(name).replace('\\', '/').rsplit('.', 1)[-1].lower()}"
        if extension in self.IMAGE_EXTENSIONS:
            return static("img/default-thumb.jpg")
        return ""

    def _save(self, name, content):
        path = self._clean_path(name)
        file_size = content.size
        content.seek(0)

        if file_size <= self.CHUNK_SIZE:
            self.client.files_upload(content.read(), path, mode=WriteMode.overwrite)
            cache.delete(self._url_cache_key(path))
            return name

        upload = self.client.files_upload_session_start(content.read(self.CHUNK_SIZE))
        cursor = dropbox.files.UploadSessionCursor(
            session_id=upload.session_id,
            offset=content.tell(),
        )
        commit = dropbox.files.CommitInfo(path=path, mode=WriteMode.overwrite)

        while content.tell() < file_size:
            remaining = file_size - content.tell()
            if remaining <= self.CHUNK_SIZE:
                self.client.files_upload_session_finish(
                    content.read(self.CHUNK_SIZE), cursor, commit
                )
            else:
                self.client.files_upload_session_append_v2(
                    content.read(self.CHUNK_SIZE), cursor
                )
                cursor.offset = content.tell()

        cache.delete(self._url_cache_key(path))
        return name

    def get_available_name(self, name, max_length=None):
        return name

    def exists(self, name):
        try:
            self.client.files_get_metadata(self._clean_path(name))
            return True
        except dropbox.exceptions.ApiError:
            return False

    def open(self, name, mode="rb"):
        if mode not in {"r", "rb"}:
            raise ValueError("DropboxStorage only supports read mode.")
        _, response = self.client.files_download(self._clean_path(name))
        return ContentFile(response.content, name=name)

    def url(self, name):
        """Return a local signed redirect URL without blocking page rendering."""
        if not name:
            return ""
        if not self._is_configured():
            return self._fallback_url(name)
        token = signing.dumps(str(name), salt="dropbox-media")
        return reverse("dropbox_file_redirect", kwargs={"token": token})

    def temporary_url(self, name):
        """Resolve and cache Dropbox's four-hour temporary URL."""
        if not name:
            return ""
        path = self._clean_path(name)
        cache_key = self._url_cache_key(path)
        cached_url = cache.get(cache_key)
        if cached_url:
            return cached_url

        try:
            link = self.client.files_get_temporary_link(path).link
        except Exception as exc:
            logger.warning("Unable to generate Dropbox URL for %s: %s", path, exc)
            fallback_url = self._fallback_url(name)
            if fallback_url:
                cache.set(cache_key, fallback_url, self.MISSING_URL_CACHE_SECONDS)
            return fallback_url

        cache.set(cache_key, link, self.URL_CACHE_SECONDS)
        return link

    def delete(self, name):
        path = self._clean_path(name)
        try:
            self.client.files_delete_v2(path)
        except dropbox.exceptions.ApiError:
            pass
        finally:
            cache.delete(self._url_cache_key(path))

    def size(self, name):
        return self.client.files_get_metadata(self._clean_path(name)).size
