from django.contrib.auth import get_user_model
from django.test import TestCase
from apps.documents.forms import CollectionForm, DocumentForm
from apps.documents.models import Collection, Document

User = get_user_model()

class CollectionFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )

    def test_collection_form_is_valid_with_required_data(self):
        form = CollectionForm(
            data={
                'name': 'Projects',
                'slug': 'projects',
                'icon': 'bi-folder',
            },
            owner=self.user
        )

        self.assertTrue(form.is_valid())

    def test_collection_form_generates_slug_when_empty(self):
        form = CollectionForm(
            data={
                'name': 'My Projects',
                'slug': '',
                'icon': 'bi-folder',
            },
            owner=self.user
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['slug'],
            'my-projects'
        )

    def test_collection_form_rejects_duplicate_root_slug(self):
        Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        form = CollectionForm(
            data={
                'name': 'Another Projects',
                'slug': 'projects',
                'icon': 'bi-folder',
            },
            owner=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)

    def test_collection_form_allows_same_root_slug_for_different_owner(self):
        Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        form = CollectionForm(
            data={
                'name': 'Projects',
                'slug': 'projects',
                'icon': 'bi-folder',
            },
            owner=self.other_user
        )

        self.assertTrue(form.is_valid())

    def test_collection_form_rejects_parent_from_another_owner(self):
        parent = Collection.objects.create(
            owner=self.other_user,
            name='Projects',
            slug='projects'
        )

        form = CollectionForm(
            data={
                'name': 'Backend',
                'slug': 'backend',
                'icon': 'bi-folder',
                'parent': parent.pk,
            },
            owner=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('parent', form.errors)

    def test_collection_form_rejects_self_parent(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        form = CollectionForm(
            data={
                'name': 'Projects',
                'slug': 'projects',
                'icon': 'bi-folder',
                'parent': collection.pk,
            },
            owner=self.user,
            instance=collection
        )

        self.assertFalse(form.is_valid())
        self.assertIn('parent', form.errors)

    def test_collection_form_limits_parent_queryset_to_owner(self):
        own_parent = Collection.objects.create(
            owner=self.user,
            name='Own',
            slug='own'
        )

        other_parent = Collection.objects.create(
            owner=self.other_user,
            name='Other',
            slug='other'
        )

        form = CollectionForm(
            owner=self.user
        )

        self.assertIn(
            own_parent,
            form.fields['parent'].queryset
        )

        self.assertNotIn(
            other_parent,
            form.fields['parent'].queryset
        )

    def test_collection_form_edit_allows_keeping_current_slug(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        form = CollectionForm(
            data={
                'name': 'Updated Projects',
                'slug': 'projects',
                'icon': 'bi-folder',
            },
            owner=self.user,
            instance=collection
        )

        self.assertTrue(form.is_valid())

    def test_collection_form_edit_preserves_slug_when_name_changes(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        form = CollectionForm(
            data={
                'name': 'Updated Projects',
                'slug': 'projects',
                'icon': 'bi-folder',
            },
            owner=self.user,
            instance=collection
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['slug'],
            'projects'
        )

    def test_collection_form_edit_rejects_existing_slug(self):
        first = Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        second = Collection.objects.create(
            owner=self.user,
            name='Archive',
            slug='archive'
        )

        form = CollectionForm(
            data={
                'name': 'Updated Archive',
                'slug': first.slug,
                'icon': 'bi-folder',
            },
            owner=self.user,
            instance=second
        )

        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)


class DocumentFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )

    def test_document_form_is_valid_with_required_data(self):
        form = DocumentForm(
            data={
                'title': 'My Document',
                'slug': 'my-document',
                'content': 'Hello',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            },
            owner=self.user
        )

        self.assertTrue(form.is_valid())

    def test_document_form_generates_slug_when_empty(self):
        form = DocumentForm(
            data={
                'title': 'My Document',
                'slug': '',
                'content': '',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            },
            owner=self.user
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['slug'],
            'my-document'
        )

    def test_document_form_rejects_duplicate_root_slug(self):
        Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='my-document'
        )

        form = DocumentForm(
            data={
                'title': 'Another Document',
                'slug': 'my-document',
                'content': '',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            },
            owner=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)

    def test_document_form_allows_same_root_slug_for_different_owner(self):
        Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='my-document'
        )

        form = DocumentForm(
            data={
                'title': 'My Document',
                'slug': 'my-document',
                'content': '',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            },
            owner=self.other_user
        )

        self.assertTrue(form.is_valid())

    def test_document_form_rejects_parent_from_another_owner(self):
        parent = Document.objects.create(
            owner=self.other_user,
            title='Parent',
            slug='parent'
        )

        form = DocumentForm(
            data={
                'title': 'Child',
                'slug': 'child',
                'content': '',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
                'parent': parent.pk,
            },
            owner=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('parent', form.errors)

    def test_document_form_rejects_collection_from_another_owner(self):
        collection = Collection.objects.create(
            owner=self.other_user,
            name='Projects',
            slug='projects'
        )

        form = DocumentForm(
            data={
                'title': 'Document',
                'slug': 'document',
                'content': '',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
                'collection': collection.pk,
            },
            owner=self.user
        )

        self.assertFalse(form.is_valid())
        self.assertIn('collection', form.errors)

    def test_document_form_rejects_self_parent(self):
        document = Document.objects.create(
            owner=self.user,
            title='Document',
            slug='document'
        )

        form = DocumentForm(
            data={
                'title': 'Document',
                'slug': 'document',
                'content': '',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
                'parent': document.pk,
            },
            owner=self.user,
            instance=document
        )

        self.assertFalse(form.is_valid())
        self.assertIn('parent', form.errors)

    def test_document_form_limits_parent_queryset_to_owner(self):
        own_parent = Document.objects.create(
            owner=self.user,
            title='Own',
            slug='own'
        )

        other_parent = Document.objects.create(
            owner=self.other_user,
            title='Other',
            slug='other'
        )

        form = DocumentForm(
            owner=self.user
        )

        self.assertIn(
            own_parent,
            form.fields['parent'].queryset
        )

        self.assertNotIn(
            other_parent,
            form.fields['parent'].queryset
        )

    def test_document_form_limits_collection_queryset_to_owner(self):
        own_collection = Collection.objects.create(
            owner=self.user,
            name='Own',
            slug='own'
        )

        other_collection = Collection.objects.create(
            owner=self.other_user,
            name='Other',
            slug='other'
        )

        form = DocumentForm(
            owner=self.user
        )

        self.assertIn(
            own_collection,
            form.fields['collection'].queryset
        )

        self.assertNotIn(
            other_collection,
            form.fields['collection'].queryset
        )

    def test_document_form_edit_allows_keeping_current_slug(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='my-document'
        )

        form = DocumentForm(
            data={
                'title': 'Updated Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            },
            owner=self.user,
            instance=document
        )

        self.assertTrue(form.is_valid())

    def test_document_form_edit_preserves_slug_when_title_changes(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='my-document'
        )

        form = DocumentForm(
            data={
                'title': 'Updated Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            },
            owner=self.user,
            instance=document
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['slug'],
            'my-document'
        )

    def test_document_form_edit_rejects_existing_slug(self):
        Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='my-document'
        )

        second = Document.objects.create(
            owner=self.user,
            title='Another Document',
            slug='another-document'
        )

        form = DocumentForm(
            data={
                'title': 'Updated Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            },
            owner=self.user,
            instance=second
        )

        self.assertFalse(form.is_valid())
        self.assertIn('slug', form.errors)