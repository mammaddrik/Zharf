from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from apps.documents.models import Collection, Document


User = get_user_model()


class CollectionModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

    def test_collection_can_be_created(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        self.assertEqual(
            collection.name,
            'Development'
        )

    def test_collection_uses_uuid_primary_key(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        self.assertIsNotNone(
            collection.pk
        )

        self.assertEqual(
            collection.pk.version,
            4
        )

    def test_collection_belongs_to_owner(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        self.assertEqual(
            collection.owner,
            self.user
        )

    def test_collection_generates_slug_from_name(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='My Development Notes'
        )

        self.assertEqual(
            collection.slug,
            'my-development-notes'
        )

    def test_collection_preserves_existing_slug(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development',
            slug='custom-slug'
        )

        self.assertEqual(
            collection.slug,
            'custom-slug'
        )

    def test_collection_has_default_icon(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        self.assertEqual(
            collection.icon,
            'bi-folder'
        )

    def test_collection_parent_is_optional(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        self.assertIsNone(
            collection.parent
        )

    def test_collection_can_have_parent(self):
        parent = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        child = Collection.objects.create(
            owner=self.user,
            name='Backend',
            parent=parent
        )

        self.assertEqual(
            child.parent,
            parent
        )

    def test_collection_parent_exposes_children(self):
        parent = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        child = Collection.objects.create(
            owner=self.user,
            name='Backend',
            parent=parent
        )

        self.assertIn(
            child,
            parent.children.all()
        )

    def test_root_collection_slug_must_be_unique_per_owner(self):
        Collection.objects.create(
            owner=self.user,
            name='Development',
            slug='development'
        )

        with self.assertRaises(IntegrityError):
            Collection.objects.create(
                owner=self.user,
                name='Another Development',
                slug='development'
            )

    def test_child_collection_slug_must_be_unique_per_parent(self):
        parent = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        Collection.objects.create(
            owner=self.user,
            name='Backend',
            parent=parent,
            slug='backend'
        )

        with self.assertRaises(IntegrityError):
            Collection.objects.create(
                owner=self.user,
                name='Another Backend',
                parent=parent,
                slug='backend'
            )

    def test_same_root_slug_is_allowed_for_different_owners(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )

        Collection.objects.create(
            owner=self.user,
            name='Development',
            slug='development'
        )

        collection = Collection.objects.create(
            owner=other_user,
            name='Development',
            slug='development'
        )

        self.assertEqual(
            collection.slug,
            'development'
        )

    def test_same_child_slug_is_allowed_under_different_parents(self):
        parent_one = Collection.objects.create(
            owner=self.user,
            name='Development One'
        )

        parent_two = Collection.objects.create(
            owner=self.user,
            name='Development Two'
        )

        Collection.objects.create(
            owner=self.user,
            name='Backend',
            parent=parent_one,
            slug='backend'
        )

        collection = Collection.objects.create(
            owner=self.user,
            name='Backend',
            parent=parent_two,
            slug='backend'
        )

        self.assertEqual(
            collection.slug,
            'backend'
        )

    def test_collection_has_created_at(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        self.assertIsNotNone(
            collection.created_at
        )

    def test_collection_has_updated_at(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        self.assertIsNotNone(
            collection.updated_at
        )

    def test_collection_updated_at_changes_on_save(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        original_updated_at = collection.updated_at

        collection.name = 'Updated Development'
        collection.save()

        collection.refresh_from_db()

        self.assertGreaterEqual(
            collection.updated_at,
            original_updated_at
        )

    def test_deleting_owner_deletes_collections(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        collection_id = collection.pk

        self.user.delete()

        self.assertFalse(
            Collection.objects.filter(
                pk=collection_id
            ).exists()
        )


class DocumentModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

    def test_document_can_be_created(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertEqual(
            document.title,
            'My Document'
        )

    def test_document_uses_uuid_primary_key(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertIsNotNone(
            document.pk
        )

        self.assertEqual(
            document.pk.version,
            4
        )

    def test_document_belongs_to_owner(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertEqual(
            document.owner,
            self.user
        )

    def test_document_generates_slug_from_title(self):
        document = Document.objects.create(
            owner=self.user,
            title='My First Document'
        )

        self.assertEqual(
            document.slug,
            'my-first-document'
        )

    def test_document_preserves_existing_slug(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='custom-document'
        )

        self.assertEqual(
            document.slug,
            'custom-document'
        )

    def test_document_slug_does_not_change_when_title_changes(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        original_slug = document.slug

        document.title = 'Renamed Document'
        document.save()

        document.refresh_from_db()

        self.assertEqual(
            document.slug,
            original_slug
        )

    def test_document_content_is_optional(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertEqual(
            document.content,
            ''
        )

    def test_document_has_note_type_by_default(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertEqual(
            document.document_type,
            Document.DocumentType.NOTE
        )

    def test_document_has_default_icon(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertEqual(
            document.icon,
            'bi-file-text'
        )

    def test_document_parent_is_optional(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertIsNone(
            document.parent
        )

    def test_document_can_have_parent(self):
        parent = Document.objects.create(
            owner=self.user,
            title='Parent Document'
        )

        child = Document.objects.create(
            owner=self.user,
            title='Child Document',
            parent=parent
        )

        self.assertEqual(
            child.parent,
            parent
        )

    def test_document_parent_exposes_children(self):
        parent = Document.objects.create(
            owner=self.user,
            title='Parent Document'
        )

        child = Document.objects.create(
            owner=self.user,
            title='Child Document',
            parent=parent
        )

        self.assertIn(
            child,
            parent.children.all()
        )

    def test_document_can_belong_to_collection(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        document = Document.objects.create(
            owner=self.user,
            title='My Document',
            collection=collection
        )

        self.assertEqual(
            document.collection,
            collection
        )

    def test_collection_exposes_documents(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        document = Document.objects.create(
            owner=self.user,
            title='My Document',
            collection=collection
        )

        self.assertIn(
            document,
            collection.documents.all()
        )

    def test_document_collection_is_optional(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertIsNone(
            document.collection
        )

    def test_document_has_favorite_false_by_default(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertFalse(
            document.is_favorite
        )

    def test_document_has_archived_false_by_default(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertFalse(
            document.is_archived
        )

    def test_document_last_opened_at_is_optional(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertIsNone(
            document.last_opened_at
        )

    def test_document_can_store_last_opened_at(self):
        opened_at = timezone.now()

        document = Document.objects.create(
            owner=self.user,
            title='My Document',
            last_opened_at=opened_at
        )

        self.assertEqual(
            document.last_opened_at,
            opened_at
        )

    def test_document_has_created_at(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertIsNotNone(
            document.created_at
        )

    def test_document_has_updated_at(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        self.assertIsNotNone(
            document.updated_at
        )

    def test_document_updated_at_changes_on_save(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        original_updated_at = document.updated_at

        document.content = 'Updated content'
        document.save()

        document.refresh_from_db()

        self.assertGreaterEqual(
            document.updated_at,
            original_updated_at
        )

    def test_root_document_slug_must_be_unique_per_owner(self):
        Document.objects.create(
            owner=self.user,
            title='First Document',
            slug='document'
        )

        with self.assertRaises(IntegrityError):
            Document.objects.create(
                owner=self.user,
                title='Second Document',
                slug='document'
            )

    def test_child_document_slug_must_be_unique_per_parent(self):
        parent = Document.objects.create(
            owner=self.user,
            title='Parent Document'
        )

        Document.objects.create(
            owner=self.user,
            title='First Child',
            parent=parent,
            slug='child'
        )

        with self.assertRaises(IntegrityError):
            Document.objects.create(
                owner=self.user,
                title='Second Child',
                parent=parent,
                slug='child'
            )

    def test_same_root_slug_is_allowed_for_different_owners(self):
        other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )

        Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='document'
        )

        document = Document.objects.create(
            owner=other_user,
            title='My Document',
            slug='document'
        )

        self.assertEqual(
            document.slug,
            'document'
        )

    def test_same_child_slug_is_allowed_under_different_parents(self):
        parent_one = Document.objects.create(
            owner=self.user,
            title='Parent One'
        )

        parent_two = Document.objects.create(
            owner=self.user,
            title='Parent Two'
        )

        Document.objects.create(
            owner=self.user,
            title='Child',
            parent=parent_one,
            slug='child'
        )

        document = Document.objects.create(
            owner=self.user,
            title='Child',
            parent=parent_two,
            slug='child'
        )

        self.assertEqual(
            document.slug,
            'child'
        )

    def test_deleting_collection_sets_document_collection_to_null(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Development'
        )

        document = Document.objects.create(
            owner=self.user,
            title='My Document',
            collection=collection
        )

        collection.delete()

        document.refresh_from_db()

        self.assertIsNone(
            document.collection
        )

    def test_deleting_owner_deletes_documents(self):
        document = Document.objects.create(
            owner=self.user,
            title='My Document'
        )

        document_id = document.pk

        self.user.delete()

        self.assertFalse(
            Document.objects.filter(
                pk=document_id
            ).exists()
        )

    def test_deleting_parent_deletes_child_documents(self):
        parent = Document.objects.create(
            owner=self.user,
            title='Parent Document'
        )

        child = Document.objects.create(
            owner=self.user,
            title='Child Document',
            parent=parent
        )

        child_id = child.pk

        parent.delete()

        self.assertFalse(
            Document.objects.filter(
                pk=child_id
            ).exists()
        )

    def test_deleting_parent_deletes_child_collections(self):
        parent = Collection.objects.create(
            owner=self.user,
            name='Parent Collection'
        )

        child = Collection.objects.create(
            owner=self.user,
            name='Child Collection',
            parent=parent
        )

        child_id = child.pk

        parent.delete()

        self.assertFalse(
            Collection.objects.filter(
                pk=child_id
            ).exists()
        )