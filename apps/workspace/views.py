from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404, render

from apps.documents.models import Collection, Document


@login_required
def workspace(request):
    return render(
        request,
        'workspace/workspace.html'
    )


@login_required
def notes(request):

    collections = Collection.objects.filter(
        owner=request.user
    )

    collections_by_parent = {}

    for collection in collections:
        collections_by_parent.setdefault(
            collection.parent_id,
            []
        ).append(collection)

    def build_tree(parent_id=None, depth=0):

        tree = []

        children = collections_by_parent.get(
            parent_id,
            []
        )

        for collection in children:

            has_children = bool(
                collections_by_parent.get(
                    collection.pk
                )
            )

            tree.append(
                {
                    'collection': collection,
                    'depth': depth,
                    'has_children': has_children,
                }
            )

            tree.extend(
                build_tree(
                    collection.pk,
                    depth + 1
                )
            )

        return tree

    collection_tree = build_tree()

    selected_collection = request.GET.get(
        'collection'
    )

    selected_view = request.GET.get(
        'view',
        'all'
    )

    documents = Document.objects.filter(
        owner=request.user
    )

    selected_collection_object = None

    if selected_collection:

        selected_collection_object = get_object_or_404(
            Collection,
            pk=selected_collection,
            owner=request.user
        )

        documents = documents.filter(
            collection=selected_collection_object
        )

    if selected_view == 'favorites':

        documents = documents.filter(
            is_favorite=True,
            is_archived=False
        )

    elif selected_view == 'recent':
        documents = documents.filter(
            is_archived=False,
            last_opened_at__isnull=False
        ).order_by(
            '-last_opened_at'
        )

    elif selected_view == 'archive':

        documents = documents.filter(
            is_archived=True
        )

    else:

        documents = documents.filter(
            is_archived=False
        )

        selected_view = 'all'

    return render(
        request,
        'documents/workspace.html',
        {
            'documents': documents,
            'collections': collections,
            'collection_tree': collection_tree,
            'selected_collection': selected_collection_object,
            'selected_view': selected_view,
        }
    )