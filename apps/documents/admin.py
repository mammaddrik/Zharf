from django.contrib import admin

from .models import Collection, Document


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'owner',
        'parent',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'name',
        'owner__email',
    )

    list_filter = (
        'created_at',
        'updated_at',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'owner',
        'collection',
        'document_type',
        'is_favorite',
        'is_archived',
        'updated_at',
    )

    search_fields = (
        'title',
        'content',
        'owner__email',
    )

    list_filter = (
        'document_type',
        'is_favorite',
        'is_archived',
        'created_at',
        'updated_at',
    )

    prepopulated_fields = {
        'slug': ('title',)
    }