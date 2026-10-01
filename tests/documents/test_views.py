from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.documents.models import Collection, Document


User = get_user_model()


class CollectionViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )

        self.collection = Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        self.other_collection = Collection.objects.create(
            owner=self.other_user,
            name='Other',
            slug='other'
        )

    def test_collection_list_requires_authentication(self):
        response = self.client.get(
            reverse('documents:collection_list')
        )

        self.assertEqual(response.status_code, 302)

    def test_collection_list_shows_only_owned_collections(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('documents:collection_list')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.collection.name
        )
        self.assertNotContains(
            response,
            self.other_collection.name
        )

    def test_collection_create_requires_authentication(self):
        response = self.client.get(
            reverse('documents:collection_create')
        )

        self.assertEqual(response.status_code, 302)

    def test_collection_create_saves_current_owner(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('documents:collection_create'),
            data={
                'name': 'Backend',
                'slug': 'backend',
                'icon': 'bi-folder',
            }
        )

        self.assertEqual(response.status_code, 302)

        collection = Collection.objects.get(
            slug='backend'
        )

        self.assertEqual(
            collection.owner,
            self.user
        )

    def test_collection_create_redirects_to_list(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('documents:collection_create'),
            data={
                'name': 'Backend',
                'slug': 'backend',
                'icon': 'bi-folder',
            }
        )

        self.assertRedirects(
            response,
            reverse('documents:collection_list')
        )

    def test_collection_update_requires_authentication(self):
        response = self.client.get(
            reverse(
                'documents:collection_update',
                kwargs={'pk': self.collection.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_collection_update_allows_owner(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'documents:collection_update',
                kwargs={'pk': self.collection.pk}
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_collection_update_blocks_other_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                'documents:collection_update',
                kwargs={'pk': self.collection.pk}
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_collection_update_changes_data(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:collection_update',
                kwargs={'pk': self.collection.pk}
            ),
            data={
                'name': 'Updated Projects',
                'slug': 'projects',
                'icon': 'bi-archive',
            }
        )

        self.assertEqual(response.status_code, 302)

        self.collection.refresh_from_db()

        self.assertEqual(
            self.collection.name,
            'Updated Projects'
        )

        self.assertEqual(
            self.collection.icon,
            'bi-archive'
        )

    def test_collection_update_redirects_to_list(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:collection_update',
                kwargs={'pk': self.collection.pk}
            ),
            data={
                'name': 'Updated Projects',
                'slug': 'projects',
                'icon': 'bi-folder',
            }
        )

        self.assertRedirects(
            response,
            reverse('documents:collection_list')
        )

    def test_collection_delete_requires_authentication(self):
        response = self.client.post(
            reverse(
                'documents:collection_delete',
                kwargs={'pk': self.collection.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_collection_delete_allows_owner(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:collection_delete',
                kwargs={'pk': self.collection.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Collection.objects.filter(
                pk=self.collection.pk
            ).exists()
        )

    def test_collection_delete_blocks_other_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                'documents:collection_delete',
                kwargs={'pk': self.collection.pk}
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Collection.objects.filter(
                pk=self.collection.pk
            ).exists()
        )

    def test_collection_delete_redirects_to_list(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:collection_delete',
                kwargs={'pk': self.collection.pk}
            )
        )

        self.assertRedirects(
            response,
            reverse('documents:collection_list')
        )


class DocumentViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='TestPassword123!'
        )

        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='TestPassword123!'
        )

        self.collection = Collection.objects.create(
            owner=self.user,
            name='Projects',
            slug='projects'
        )

        self.parent_document = Document.objects.create(
            owner=self.user,
            title='Parent Document',
            slug='parent-document'
        )

        self.document = Document.objects.create(
            owner=self.user,
            title='My Document',
            slug='my-document',
            content='Hello'
        )

        self.other_document = Document.objects.create(
            owner=self.other_user,
            title='Other Document',
            slug='other-document',
            content='Other content'
        )

    def test_document_list_requires_authentication(self):
        response = self.client.get(
            reverse('documents:document_list')
        )

        self.assertEqual(response.status_code, 302)

    def test_document_list_shows_only_owned_documents(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('documents:document_list')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.document.title
        )
        self.assertNotContains(
            response,
            self.other_document.title
        )

    def test_document_detail_requires_authentication(self):
        response = self.client.get(
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_document_detail_allows_owner(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_document_detail_blocks_other_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_document_toggle_favorite_requires_authentication(self):
        response = self.client.post(
            reverse(
                'documents:document_toggle_favorite',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.document.refresh_from_db()

        self.assertFalse(
            self.document.is_favorite
        )

    def test_document_toggle_favorite_marks_document_as_favorite(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_toggle_favorite',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertRedirects(
            response,
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.document.refresh_from_db()

        self.assertTrue(
            self.document.is_favorite
        )

    def test_document_toggle_favorite_removes_favorite(self):
        self.document.is_favorite = True

        self.document.save(
            update_fields=['is_favorite']
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_toggle_favorite',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertRedirects(
            response,
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.document.refresh_from_db()

        self.assertFalse(
            self.document.is_favorite
        )

    def test_document_toggle_favorite_blocks_other_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                'documents:document_toggle_favorite',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.document.refresh_from_db()

        self.assertFalse(
            self.document.is_favorite
        )

    def test_document_toggle_archive_requires_authentication(self):
        response = self.client.post(
            reverse(
                'documents:document_toggle_archive',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.document.refresh_from_db()

        self.assertFalse(
            self.document.is_archived
        )

    def test_document_toggle_archive_archives_document(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_toggle_archive',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertRedirects(
            response,
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.document.refresh_from_db()

        self.assertTrue(
            self.document.is_archived
        )

    def test_document_toggle_archive_unarchives_document(self):
        self.document.is_archived = True

        self.document.save(
            update_fields=['is_archived']
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_toggle_archive',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertRedirects(
            response,
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.document.refresh_from_db()

        self.assertFalse(
            self.document.is_archived
        )

    def test_document_toggle_archive_blocks_other_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                'documents:document_toggle_archive',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(
            response.status_code,
            404
        )

        self.document.refresh_from_db()

        self.assertFalse(
            self.document.is_archived
        )

    def test_document_create_requires_authentication(self):
        response = self.client.get(
            reverse('documents:document_create')
        )

        self.assertEqual(response.status_code, 302)

    def test_document_create_saves_current_owner(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('documents:document_create'),
            data={
                'title': 'New Document',
                'slug': 'new-document',
                'content': 'New content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            }
        )

        self.assertEqual(response.status_code, 302)

        document = Document.objects.get(
            slug='new-document'
        )

        self.assertEqual(
            document.owner,
            self.user
        )

    def test_document_create_redirects_to_detail(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('documents:document_create'),
            data={
                'title': 'New Document',
                'slug': 'new-document',
                'content': 'New content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            }
        )

        document = Document.objects.get(
            slug='new-document'
        )

        self.assertRedirects(
            response,
            reverse(
                'documents:document_detail',
                kwargs={'pk': document.pk}
            )
        )

    def test_document_create_saves_collection(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('documents:document_create'),
            data={
                'title': 'Project Document',
                'slug': 'project-document',
                'content': 'Project content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
                'collection': self.collection.pk,
            }
        )

        self.assertEqual(response.status_code, 302)

        document = Document.objects.get(
            slug='project-document'
        )

        self.assertEqual(
            document.collection,
            self.collection
        )

    def test_document_create_saves_parent(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('documents:document_create'),
            data={
                'title': 'Child Document',
                'slug': 'child-document',
                'content': 'Child content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
                'parent': self.parent_document.pk,
            }
        )

        self.assertEqual(response.status_code, 302)

        document = Document.objects.get(
            slug='child-document'
        )

        self.assertEqual(
            document.parent,
            self.parent_document
        )

    def test_document_update_requires_authentication(self):
        response = self.client.get(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_document_update_allows_owner(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_document_update_blocks_other_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_document_update_changes_data(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            ),
            data={
                'title': 'Updated Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-journal-text',
            }
        )

        self.assertEqual(response.status_code, 302)

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.title,
            'Updated Document'
        )

        self.assertEqual(
            self.document.content,
            'Updated content'
        )

        self.assertEqual(
            self.document.icon,
            'bi-journal-text'
        )

    def test_document_update_preserves_slug(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            ),
            data={
                'title': 'Updated Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            }
        )

        self.assertEqual(response.status_code, 302)

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.slug,
            'my-document'
        )

    def test_document_update_saves_collection(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            ),
            data={
                'title': 'My Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
                'collection': self.collection.pk,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.collection,
            self.collection
        )

    def test_document_update_saves_parent(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            ),
            data={
                'title': 'My Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
                'parent': self.parent_document.pk,
            }
        )

        self.assertEqual(response.status_code, 302)

        self.document.refresh_from_db()

        self.assertEqual(
            self.document.parent,
            self.parent_document
        )

    def test_document_update_redirects_to_detail(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_update',
                kwargs={'pk': self.document.pk}
            ),
            data={
                'title': 'Updated Document',
                'slug': 'my-document',
                'content': 'Updated content',
                'document_type': Document.DocumentType.NOTE,
                'icon': 'bi-file-text',
            }
        )

        self.assertRedirects(
            response,
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

    def test_document_delete_requires_authentication(self):
        response = self.client.post(
            reverse(
                'documents:document_delete',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_document_delete_allows_owner(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_delete',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Document.objects.filter(
                pk=self.document.pk
            ).exists()
        )

    def test_document_delete_blocks_other_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.post(
            reverse(
                'documents:document_delete',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            Document.objects.filter(
                pk=self.document.pk
            ).exists()
        )

    def test_document_delete_redirects_to_list(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse(
                'documents:document_delete',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertRedirects(
            response,
            reverse('documents:document_list')
        )
    def test_document_detail_updates_last_opened_at(self):
        self.client.force_login(self.user)

        self.assertIsNone(
            self.document.last_opened_at
        )

        response = self.client.get(
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.document.refresh_from_db()

        self.assertIsNotNone(
            self.document.last_opened_at
        )

    def test_archived_document_detail_does_not_update_last_opened_at(self):
        self.document.is_archived = True
        self.document.save(
            update_fields=['is_archived']
        )

        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                'documents:document_detail',
                kwargs={'pk': self.document.pk}
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.document.refresh_from_db()

        self.assertIsNone(
            self.document.last_opened_at
        )