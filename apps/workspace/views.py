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

    selected_collection = request.GET.get('collection')

    documents = Document.objects.filter(
        owner=request.user,
        is_archived=False
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

    return render(
        request,
        'documents/workspace.html',
        {
            'documents': documents,
            'collections': collections,
            'collection_tree': collection_tree,
            'selected_collection': selected_collection_object,
        }
    )