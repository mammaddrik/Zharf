from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TodoForm, TodoItemForm
from .models import Todo, TodoItem


@login_required
def todo_list(request):
    todos = request.user.todos.order_by(
        'completed',
        '-created_at'
    )

    form = TodoForm()

    return render(
        request,
        'todos/todo_list.html',
        {
            'todos': todos,
            'form': form,
        }
    )


@login_required
def todo_create(request):
    if request.method != 'POST':
        return redirect('todo_list')

    form = TodoForm(request.POST)

    if form.is_valid():
        subtasks = [
            title.strip()
            for title in request.POST.getlist('subtasks')
            if title.strip()
        ]

        with transaction.atomic():
            todo = form.save(commit=False)
            todo.owner = request.user
            todo.save()

            TodoItem.objects.bulk_create([
                TodoItem(
                    todo=todo,
                    title=title,
                    position=position
                )
                for position, title in enumerate(subtasks)
            ])

    return redirect('todo_list')


@login_required
def todo_edit(request, todo_id):
    todo = get_object_or_404(
        Todo,
        id=todo_id,
        owner=request.user
    )

    if request.method == 'POST':
        form = TodoForm(
            request.POST,
            instance=todo
        )

        if form.is_valid():
            subtasks = [
                title.strip()
                for title in request.POST.getlist('subtasks')
                if title.strip()
            ]

            with transaction.atomic():
                form.save()

                TodoItem.objects.bulk_create([
                    TodoItem(
                        todo=todo,
                        title=title,
                        position=position
                    )
                    for position, title in enumerate(
                        subtasks,
                        start=todo.items.count()
                    )
                ])

                TodoItem.sync_todo_status(todo)

            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)

    return render(
        request,
        'todos/todo_edit.html',
        {
            'todo': todo,
            'form': form,
            'item_form': TodoItemForm(),
        }
    )


@login_required
def todo_toggle(request, todo_id):
    if request.method != 'POST':
        raise Http404

    todo = get_object_or_404(
        Todo,
        id=todo_id,
        owner=request.user
    )

    todo.completed = not todo.completed

    if todo.completed:
        todo.completed_at = timezone.now()
    else:
        todo.completed_at = None

    todo.save(
        update_fields=[
            'completed',
            'completed_at',
            'updated_at',
        ]
    )

    return redirect('todo_list')


@login_required
def todo_delete(request, todo_id):
    if request.method != 'POST':
        raise Http404

    todo = get_object_or_404(
        Todo,
        id=todo_id,
        owner=request.user
    )

    todo.delete()

    return redirect('todo_list')



@login_required
def todo_item_create(request, todo_id):
    if request.method != 'POST':
        raise Http404

    todo = get_object_or_404(
        Todo,
        id=todo_id,
        owner=request.user
    )

    form = TodoItemForm(request.POST)

    if form.is_valid():
        item = form.save(commit=False)
        item.todo = todo
        item.position = todo.items.count()
        item.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'item_id': str(item.id),
                'title': item.title,
                'completed': item.completed,
                'position': item.position,
            })

        return redirect('todo_list')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors.get_json_data(),
        }, status=400)

    return redirect('todo_list')



@login_required
def todo_item_toggle(request, todo_id, item_id):
    if request.method != 'POST':
        raise Http404

    item = get_object_or_404(
        TodoItem,
        id=item_id,
        todo__id=todo_id,
        todo__owner=request.user
    )

    item.completed = not item.completed
    item.save(update_fields=['completed'])

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_id': item.id,
            'completed': item.completed,
        })

    return redirect('todo_list')


@login_required
def todo_item_delete(request, todo_id, item_id):
    if request.method != 'POST':
        raise Http404

    item = get_object_or_404(
        TodoItem,
        id=item_id,
        todo__id=todo_id,
        todo__owner=request.user
    )

    deleted_item_id = item.id
    item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_id': deleted_item_id,
        })

    return redirect('todo_list')


@login_required
def todo_item_reorder(request, todo_id):
    if request.method != 'POST':
        raise Http404

    todo = get_object_or_404(
        Todo,
        id=todo_id,
        owner=request.user
    )

    item_ids = request.POST.getlist('item_ids[]')

    existing_ids = {
        str(item_id)
        for item_id in todo.items.values_list('id', flat=True)
    }
    submitted_ids = set(item_ids)

    if (
        len(item_ids) != len(submitted_ids)
        or submitted_ids != existing_ids
    ):
        return JsonResponse(
            {
                'success': False,
                'error': 'Invalid item IDs.',
            },
            status=400
        )

    items_by_id = {
        str(item.id): item
        for item in todo.items.all()
    }

    with transaction.atomic():
        for position, item_id in enumerate(item_ids):
            item = items_by_id[item_id]

            if item.position != position:
                item.position = position
                item.save(update_fields=['position'])

    return JsonResponse({'success': True})
