from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CollectionForm, DocumentForm
from .models import Collection, Document


@login_required
def collection_list(request):
    collections = Collection.objects.filter(
        owner=request.user
    )

    return render(
        request,
        'documents/collections/list.html',
        {
            'collections': collections,
        }
    )


@login_required
def collection_create(request):
    if request.method == 'POST':
        form = CollectionForm(
            request.POST,
            owner=request.user
        )

        if form.is_valid():
            collection = form.save(commit=False)
            collection.owner = request.user
            collection.save()

            return redirect('documents:collection_list')
    else:
        form = CollectionForm(
            owner=request.user
        )

    return render(
        request,
        'documents/collections/form.html',
        {
            'form': form,
        }
    )


@login_required
def collection_update(request, pk):
    collection = get_object_or_404(
        Collection,
        pk=pk,
        owner=request.user
    )

    if request.method == 'POST':
        form = CollectionForm(
            request.POST,
            instance=collection,
            owner=request.user
        )

        if form.is_valid():
            form.save()

            return redirect('documents:collection_list')
    else:
        form = CollectionForm(
            instance=collection,
            owner=request.user
        )

    return render(
        request,
        'documents/collections/form.html',
        {
            'form': form,
            'collection': collection,
        }
    )


@login_required
def collection_delete(request, pk):
    collection = get_object_or_404(
        Collection,
        pk=pk,
        owner=request.user
    )

    if request.method == 'POST':
        collection.delete()

        return redirect('documents:collection_list')

    return render(
        request,
        'documents/collections/delete.html',
        {
            'collection': collection,
        }
    )


@login_required
def document_list(request):
    documents = Document.objects.filter(
        owner=request.user
    )

    return render(
        request,
        'documents/list.html',
        {
            'documents': documents,
        }
    )


@login_required
def document_detail(request, pk):
    document = get_object_or_404(
        Document,
        pk=pk,
        owner=request.user
    )

    return render(
        request,
        'documents/detail.html',
        {
            'document': document,
        }
    )


@login_required
def document_create(request):
    if request.method == 'POST':
        form = DocumentForm(
            request.POST,
            owner=request.user
        )

        if form.is_valid():
            document = form.save(commit=False)
            document.owner = request.user
            document.save()

            return redirect(
                'documents:document_detail',
                pk=document.pk
            )
    else:
        form = DocumentForm(
            owner=request.user
        )

    return render(
        request,
        'documents/form.html',
        {
            'form': form,
        }
    )


@login_required
def document_update(request, pk):
    document = get_object_or_404(
        Document,
        pk=pk,
        owner=request.user
    )

    if request.method == 'POST':
        form = DocumentForm(
            request.POST,
            instance=document,
            owner=request.user
        )

        if form.is_valid():
            form.save()

            return redirect(
                'documents:document_detail',
                pk=document.pk
            )
    else:
        form = DocumentForm(
            instance=document,
            owner=request.user
        )

    return render(
        request,
        'documents/form.html',
        {
            'form': form,
            'document': document,
        }
    )


@login_required
def document_delete(request, pk):
    document = get_object_or_404(
        Document,
        pk=pk,
        owner=request.user
    )

    if request.method == 'POST':
        document.delete()

        return redirect('documents:document_list')

    return render(
        request,
        'documents/delete.html',
        {
            'document': document,
        }
    )