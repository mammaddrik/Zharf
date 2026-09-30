from django import forms
from django.utils.text import slugify

from .models import Collection, Document


class CollectionForm(forms.ModelForm):

    class Meta:
        model = Collection
        fields = [
            'name',
            'slug',
            'icon',
            'parent',
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Collection name',
                }
            ),
            'slug': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'collection-name',
                    'spellcheck': 'false',
                }
            ),
            'icon': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'bi-folder',
                    'spellcheck': 'false',
                }
            ),
            'parent': forms.Select(
                attrs={
                    'class': 'form-input',
                }
            ),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['slug'].required = False

        self.owner = owner

        self.fields['parent'].queryset = Collection.objects.none()

        if owner is not None:
            queryset = Collection.objects.filter(
                owner=owner
            )

            if self.instance.pk:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            self.fields['parent'].queryset = queryset

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')

        if not slug:
            slug = slugify(
                self.cleaned_data.get('name', '')
            )

        return slug

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')

        if parent is None:
            return parent

        if self.owner is None or parent.owner_id != self.owner.pk:
            raise forms.ValidationError(
                'Invalid parent collection.'
            )

        if self.instance.pk and parent.pk == self.instance.pk:
            raise forms.ValidationError(
                'A collection cannot be its own parent.'
            )

        return parent

    def clean(self):
        cleaned_data = super().clean()

        slug = cleaned_data.get('slug')
        parent = cleaned_data.get('parent')

        if slug and self.owner is not None:
            queryset = Collection.objects.filter(
                owner=self.owner,
                slug=slug,
            )

            if parent is None:
                queryset = queryset.filter(
                    parent__isnull=True
                )
            else:
                queryset = queryset.filter(
                    parent=parent
                )

            if self.instance.pk:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                self.add_error(
                    'slug',
                    'A collection with this slug already exists here.'
                )

        return cleaned_data


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = [
            'title',
            'slug',
            'content',
            'document_type',
            'icon',
            'parent',
            'collection',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Document title',
                }
            ),
            'slug': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'document-title',
                    'spellcheck': 'false',
                }
            ),
            'content': forms.Textarea(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Write your document...',
                    'rows': 12,
                }
            ),
            'document_type': forms.Select(
                attrs={
                    'class': 'form-input',
                }
            ),
            'icon': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'bi-file-text',
                    'spellcheck': 'false',
                }
            ),
            'parent': forms.Select(
                attrs={
                    'class': 'form-input',
                }
            ),
            'collection': forms.Select(
                attrs={
                    'class': 'form-input',
                }
            ),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['slug'].required = False

        self.owner = owner

        self.fields['parent'].queryset = Document.objects.none()
        self.fields['collection'].queryset = Collection.objects.none()

        if owner is not None:
            parent_queryset = Document.objects.filter(
                owner=owner
            )

            collection_queryset = Collection.objects.filter(
                owner=owner
            )

            if self.instance.pk:
                parent_queryset = parent_queryset.exclude(
                    pk=self.instance.pk
                )

            self.fields['parent'].queryset = parent_queryset
            self.fields['collection'].queryset = collection_queryset

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')

        if not slug:
            slug = slugify(
                self.cleaned_data.get('title', '')
            )

        return slug

    def clean_parent(self):
        parent = self.cleaned_data.get('parent')

        if parent is None:
            return parent

        if self.owner is None or parent.owner_id != self.owner.pk:
            raise forms.ValidationError(
                'Invalid parent document.'
            )

        if self.instance.pk and parent.pk == self.instance.pk:
            raise forms.ValidationError(
                'A document cannot be its own parent.'
            )

        return parent

    def clean_collection(self):
        collection = self.cleaned_data.get('collection')

        if collection is None:
            return collection

        if (
            self.owner is None
            or collection.owner_id != self.owner.pk
        ):
            raise forms.ValidationError(
                'Invalid collection.'
            )

        return collection

    def clean(self):
        cleaned_data = super().clean()

        slug = cleaned_data.get('slug')
        parent = cleaned_data.get('parent')

        if slug and self.owner is not None:
            queryset = Document.objects.filter(
                owner=self.owner,
                slug=slug,
            )

            if parent is None:
                queryset = queryset.filter(
                    parent__isnull=True
                )
            else:
                queryset = queryset.filter(
                    parent=parent
                )

            if self.instance.pk:
                queryset = queryset.exclude(
                    pk=self.instance.pk
                )

            if queryset.exists():
                self.add_error(
                    'slug',
                    'A document with this slug already exists here.'
                )

        return cleaned_data