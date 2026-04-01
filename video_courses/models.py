from django.db import models
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.conf import settings
from .dropbox_storage import DropboxStorage

# Initialize Dropbox storage
dropbox_storage = DropboxStorage()

# Optional: media duration extraction with moviepy
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except Exception:
    MOVIEPY_AVAILABLE = False


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimestampedModel):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        return super().save(*args, **kwargs)


# Upload paths
def course_thumb_upload(instance, filename):
    slug = instance.slug or slugify(instance.name)[:220] or "course"
    return f"video_courses/{slug}/thumbs/{filename}"


def course_video_upload(instance, filename):
    slug = instance.course.slug or slugify(instance.course.name)[:220] or "course"
    return f"video_courses/{slug}/videos/{filename}"


class VideoCourse(TimestampedModel):
    name = models.CharField(max_length=220, unique=True)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="video_courses"
    )

    description = models.TextField(blank=True)

    thumbnail = models.ImageField(
        upload_to=course_thumb_upload,
        storage=dropbox_storage,
        blank=True,
        null=True
    )

    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default="INR")

    instructor_name = models.CharField(max_length=160, default="Sadok Sniine")
    instructor_headline = models.CharField(
        max_length=220,
        default="Physics Professor · 15+ years of teaching"
    )

    instructor_avatar = models.ImageField(
        upload_to="video_courses/instructors/",
        storage=dropbox_storage,
        blank=True,
        null=True
    )

    is_premium = models.BooleanField(default=True)
    is_free = models.BooleanField(
        default=False,
        help_text="If checked, course is free. Otherwise, it's paid."
    )
    is_bestseller = models.BooleanField(default=False)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.PositiveIntegerField(default=0)

    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def course_type(self):
        return "Free" if self.is_free else "Paid"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:240]

        if self.is_free:
            self.selling_price = 0

        return super().save(*args, **kwargs)


class WhatYouLearnPoint(TimestampedModel):
    course = models.ForeignKey(
        VideoCourse,
        on_delete=models.CASCADE,
        related_name="learn_points"
    )
    text = models.CharField(max_length=280)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.course.name} - {self.text[:40]}"


class CourseInclude(TimestampedModel):
    course = models.ForeignKey(
        VideoCourse,
        on_delete=models.CASCADE,
        related_name="includes"
    )
    label = models.CharField(max_length=200)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.course.name} - {self.label}"


class CourseVideo(TimestampedModel):
    course = models.ForeignKey(
        VideoCourse,
        on_delete=models.CASCADE,
        related_name="videos"
    )

    title = models.CharField(max_length=220)
    duration_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Auto-detected on save"
    )

    is_preview = models.BooleanField(default=False)

    file = models.FileField(
        upload_to=course_video_upload,
        storage=dropbox_storage
    )

    thumb_image = models.ImageField(
        upload_to="video_courses/video_thumbs/",
        storage=dropbox_storage,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.course.name} - {self.title}"

    def save(self, *args, **kwargs):
        # First save so file is uploaded
        super().save(*args, **kwargs)

        # Extract duration if not already set
        if self.file and self.duration_seconds in (0, None) and MOVIEPY_AVAILABLE:
            try:
                file_path = None

                # If local path exists (unlikely in Dropbox)
                if hasattr(self.file, "path"):
                    file_path = self.file.path

                # Otherwise download temporarily
                if not file_path:
                    tmp_name = f"_tmp_{self.pk}.media"
                    with default_storage.open(self.file.name, "rb") as src:
                        with open(tmp_name, "wb") as dst:
                            dst.write(src.read())
                    file_path = tmp_name

                from moviepy.editor import VideoFileClip
                with VideoFileClip(file_path) as clip:
                    duration = int(round(clip.duration or 0))
                    if duration > 0 and duration != self.duration_seconds:
                        self.duration_seconds = duration
                        super().save(update_fields=["duration_seconds"])

                # Cleanup temp file
                if file_path and file_path.startswith("_tmp_"):
                    import os
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass

            except Exception:
                pass