from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.documents.models import Collection, Document


User = get_user_model()


class NotesViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='StrongPassword123!'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='StrongPassword123!'
        )

    def test_notes_requires_authentication(self):
        response = self.client.get(
            reverse('notes')
        )

        self.assertRedirects(
            response,
            '/accounts/signin/?next=/workspace/notes/'
        )

    def test_notes_only_shows_owned_collections(self):
        owned_collection = Collection.objects.create(
            owner=self.user,
            name='Owned',
            slug='owned'
        )

        other_collection = Collection.objects.create(
            owner=self.other_user,
            name='Other',
            slug='other'
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, owned_collection.name)
        self.assertNotContains(response, other_collection.name)

    def test_notes_only_shows_owned_documents(self):
        owned_document = Document.objects.create(
            owner=self.user,
            title='Owned Document',
            slug='owned-document'
        )

        other_document = Document.objects.create(
            owner=self.other_user,
            title='Other Document',
            slug='other-document'
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, owned_document.title)
        self.assertNotContains(response, other_document.title)

    def test_notes_excludes_archived_documents(self):
        active_document = Document.objects.create(
            owner=self.user,
            title='Active Document',
            slug='active-document'
        )

        archived_document = Document.objects.create(
            owner=self.user,
            title='Archived Document',
            slug='archived-document',
            is_archived=True
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, active_document.title)
        self.assertNotContains(response, archived_document.title)

    def test_notes_filters_documents_by_collection(self):
        first_collection = Collection.objects.create(
            owner=self.user,
            name='First',
            slug='first'
        )

        second_collection = Collection.objects.create(
            owner=self.user,
            name='Second',
            slug='second'
        )

        first_document = Document.objects.create(
            owner=self.user,
            title='First Document',
            slug='first-document',
            collection=first_collection
        )

        second_document = Document.objects.create(
            owner=self.user,
            title='Second Document',
            slug='second-document',
            collection=second_collection
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes'),
            {
                'collection': first_collection.pk
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, first_document.title)
        self.assertNotContains(response, second_document.title)

    def test_notes_rejects_collection_owned_by_another_user(self):
        collection = Collection.objects.create(
            owner=self.other_user,
            name='Other Collection',
            slug='other-collection'
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes'),
            {
                'collection': collection.pk
            }
        )

        self.assertEqual(response.status_code, 404)

    def test_notes_without_collection_has_no_selected_collection(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes')
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            response.context['selected_collection']
        )

    def test_notes_with_collection_passes_selected_collection_to_context(self):
        collection = Collection.objects.create(
            owner=self.user,
            name='Selected',
            slug='selected'
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes'),
            {
                'collection': collection.pk
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['selected_collection'],
            collection
        )
    def test_notes_builds_collection_tree(self):
        root_collection = Collection.objects.create(
            owner=self.user,
            name='Work',
            slug='work'
        )

        child_collection = Collection.objects.create(
            owner=self.user,
            name='Backend',
            slug='backend',
            parent=root_collection
        )

        grandchild_collection = Collection.objects.create(
            owner=self.user,
            name='Django',
            slug='django',
            parent=child_collection
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes')
        )

        self.assertEqual(response.status_code, 200)

        collection_tree = response.context['collection_tree']

        self.assertEqual(
            collection_tree[0]['collection'],
            root_collection
        )

        self.assertEqual(
            collection_tree[0]['depth'],
            0
        )

        self.assertEqual(
            collection_tree[1]['collection'],
            child_collection
        )

        self.assertEqual(
            collection_tree[1]['depth'],
            1
        )

        self.assertEqual(
            collection_tree[2]['collection'],
            grandchild_collection
        )

        self.assertEqual(
            collection_tree[2]['depth'],
            2
        )


    def test_notes_collection_tree_only_contains_owned_collections(self):
        owned_root = Collection.objects.create(
            owner=self.user,
            name='Owned',
            slug='owned'
        )

        owned_child = Collection.objects.create(
            owner=self.user,
            name='Owned Child',
            slug='owned-child',
            parent=owned_root
        )

        Collection.objects.create(
            owner=self.other_user,
            name='Other',
            slug='other'
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse('notes')
        )

        self.assertEqual(response.status_code, 200)

        collection_tree = response.context['collection_tree']

        tree_collections = [
            item['collection']
            for item in collection_tree
        ]

        self.assertIn(
            owned_root,
            tree_collections
        )

        self.assertIn(
            owned_child,
            tree_collections
        )

        self.assertEqual(
            len(tree_collections),
            2
        )