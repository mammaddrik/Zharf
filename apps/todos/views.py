from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import TodoForm
from .models import Todo


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
        todo = form.save(commit=False)
        todo.owner = request.user
        todo.save()

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
            form.save()
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)

    return render(
        request,
        'todos/todo_edit.html',
        {
            'todo': todo,
            'form': form,
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