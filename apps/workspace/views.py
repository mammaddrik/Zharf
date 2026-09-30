from django.contrib.auth.decorators import login_required
from django.shortcuts import render
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
            'selected_collection': selected_collection_object,
        }
    )