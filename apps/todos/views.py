
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

    print("Logged-in user:", request.user)
    print("User Todo count:", todos.count())

    for todo in todos:
        print(
            "Todo:",
            todo.title,
            "| Subtasks:",
            todo.items.count()
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
                TodoItem(todo=todo, title=title)
                for title in subtasks
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
                    TodoItem(todo=todo, title=title)
                    for title in subtasks
                ])

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
        item.save()

    return redirect('todo_edit', todo_id=todo.id)


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

    return redirect('todo_edit', todo_id=todo_id)


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

    item.delete()

    return redirect('todo_edit', todo_id=todo_id)


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

    items = list(
        todo.items.filter(id__in=item_ids)
    )

    # Ensure all submitted IDs belong to this Todo,
    # with no duplicates or missing items.
    submitted_ids = set(item_ids)
    existing_ids = {str(item.id) for item in items}

    if (
        len(item_ids) != len(submitted_ids)
        or submitted_ids != existing_ids
    ):
        return JsonResponse(
            {'success': False, 'error': 'Invalid item IDs.'},
            status=400
        )

    with transaction.atomic():
        items_by_id = {str(item.id): item for item in items}

        for position, item_id in enumerate(item_ids):
            item = items_by_id[item_id]
            if item.position != position:
                item.position = position
                item.save(update_fields=['position'])

    return JsonResponse({'success': True})
