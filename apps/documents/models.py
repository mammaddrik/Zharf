import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class Collection(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections'
    )

    name = models.CharField(
        max_length=100
    )

    slug = models.SlugField(
        max_length=120
    )

    icon = models.CharField(
        max_length=100,
        default='bi-folder'
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'slug'],
                condition=Q(parent__isnull=True),
                name='unique_root_collection_slug'
            ),
            models.UniqueConstraint(
                fields=['owner', 'parent', 'slug'],
                condition=Q(parent__isnull=False),
                name='unique_child_collection_slug'
            ),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)


class Document(models.Model):

    class DocumentType(models.TextChoices):
        NOTE = 'note', 'Note'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    title = models.CharField(
        max_length=200
    )

    slug = models.SlugField(
        max_length=220
    )

    content = models.TextField(
        blank=True
    )

    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        default=DocumentType.NOTE
    )

    icon = models.CharField(
        max_length=100,
        default='bi-file-text'
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )

    collection = models.ForeignKey(
        Collection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )

    is_favorite = models.BooleanField(
        default=False
    )

    is_archived = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    last_opened_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-updated_at']
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'slug'],
                condition=Q(parent__isnull=True),
                name='unique_root_document_slug'
            ),
            models.UniqueConstraint(
                fields=['owner', 'parent', 'slug'],
                condition=Q(parent__isnull=False),
                name='unique_child_document_slug'
            ),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)