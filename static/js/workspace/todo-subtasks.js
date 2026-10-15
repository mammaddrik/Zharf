
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('todo-subtask-inputs');
    const addButton = document.getElementById('todo-add-subtask-input');
    const firstInput = document.getElementById('todo-subtask-first-input');
    const todoForm = addButton?.closest('form');

    const getCsrfToken = (form = null) => {
        const input = form?.querySelector('[name="csrfmiddlewaretoken"]')
            || document.querySelector('[name="csrfmiddlewaretoken"]');

        if (input?.value) {
            return input.value;
        }

        const cookie = document.cookie
            .split('; ')
            .find((entry) => entry.startsWith('csrftoken='));

        return cookie
            ? decodeURIComponent(cookie.substring('csrftoken='.length))
            : null;
    };

    const postAjax = async (url, csrfToken, body = null) => {
        const options = {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        };

        if (body) {
            options.body = body;
        }

        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok || data.success === false) {
            throw new Error(
                data.error || data.errors
                    ? JSON.stringify(data.errors || data.error)
                    : 'Request failed.'
            );
        }

        return data;
    };

    if (container && addButton && todoForm) {
        let draggedRow = null;

        const getRows = () => [
            ...container.querySelectorAll('.todo-subtask-input-row'),
        ];

        const getRowInput = (row) =>
            row.querySelector('input[name="subtasks"]');

        const updateRemoveButtons = () => {
            const rows = getRows();
            const showControls = rows.length > 1;

            rows.forEach((row) => {
                const removeButton = row.querySelector(
                    '.todo-subtask-remove'
                );

                const dragHandle = row.querySelector(
                    '.todo-subtask-drag-handle'
                );

                if (dragHandle) {
                    dragHandle.hidden = !showControls;
                    dragHandle.style.display = showControls
                        ? 'inline-flex'
                        : 'none';
                }

                if (removeButton) {
                    removeButton.hidden = !showControls;
                }
            });
        };

        const createSubtaskRow = (value = '') => {
            const row = document.createElement('div');
            row.className = 'todo-subtask-input-row';

            const handle = document.createElement('button');
            handle.type = 'button';
            handle.className = 'todo-subtask-drag-handle';
            handle.setAttribute('aria-label', 'Reorder subtask');
            handle.title = 'Drag to reorder';
            handle.draggable = true;
            handle.hidden = true;
            handle.style.display = 'none';

            const input = document.createElement('input');
            input.type = 'text';
            input.name = 'subtasks';
            input.className = 'todo-form-input';
            input.placeholder = 'Enter a subtask...';
            input.autocomplete = 'off';
            input.value = value;

            const removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.className = 'todo-subtask-remove';
            removeButton.setAttribute('aria-label', 'Remove subtask');

            const icon = document.createElement('i');
            icon.className = 'bi bi-trash3';
            icon.setAttribute('aria-hidden', 'true');
            removeButton.appendChild(icon);

            row.append(handle, input, removeButton);

            return row;
        };

        const addSubtaskRow = (value = '') => {
            const row = createSubtaskRow(value);
            container.appendChild(row);
            updateRemoveButtons();

            return row;
        };

        if (firstInput) {
            addButton.addEventListener('click', () => {
                addSubtaskRow(firstInput.value.trim());
                firstInput.value = '';
                firstInput.focus();
            });

            firstInput.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    addButton.click();
                }
            });
        } else {
            addButton.addEventListener('click', () => {
                const row = addSubtaskRow();
                getRowInput(row)?.focus();
            });
        }

        container.addEventListener('click', (event) => {
            const removeButton = event.target.closest(
                '.todo-subtask-remove'
            );

            if (!removeButton || !container.contains(removeButton)) {
                return;
            }

            removeButton.closest('.todo-subtask-input-row')?.remove();
            updateRemoveButtons();
        });

        container.addEventListener('dragstart', (event) => {
            const handle = event.target.closest(
                '.todo-subtask-drag-handle'
            );

            if (!handle || handle.hidden) {
                event.preventDefault();
                return;
            }

            draggedRow = handle.closest('.todo-subtask-input-row');

            if (!draggedRow) {
                event.preventDefault();
                return;
            }

            draggedRow.classList.add('is-dragging');

            if (event.dataTransfer) {
                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', 'subtask');
            }
        });

        container.addEventListener('dragover', (event) => {
            if (!draggedRow) {
                return;
            }

            event.preventDefault();

            const targetRow = event.target.closest(
                '.todo-subtask-input-row'
            );

            if (
                !targetRow ||
                targetRow === draggedRow ||
                !container.contains(targetRow)
            ) {
                return;
            }

            const rect = targetRow.getBoundingClientRect();
            const insertAfter =
                event.clientY > rect.top + rect.height / 2;

            if (insertAfter) {
                targetRow.after(draggedRow);
            } else {
                targetRow.before(draggedRow);
            }
        });

        container.addEventListener('drop', (event) => {
            if (draggedRow) {
                event.preventDefault();
            }
        });

        container.addEventListener('dragend', () => {
            if (draggedRow) {
                draggedRow.classList.remove('is-dragging');
                draggedRow = null;
            }

            updateRemoveButtons();
        });

        todoForm.addEventListener('submit', () => {
            if (firstInput) {
                const firstValue = firstInput.value.trim();
                const firstRow = getRows()[0];

                if (firstValue) {
                    if (firstRow) {
                        const firstRowInput = getRowInput(firstRow);

                        if (firstRowInput) {
                            firstRowInput.value = firstValue;
                        } else {
                            const hiddenInput = document.createElement('input');
                            hiddenInput.type = 'hidden';
                            hiddenInput.name = 'subtasks';
                            hiddenInput.value = firstValue;
                            firstRow.appendChild(hiddenInput);
                        }
                    } else {
                        const hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.name = 'subtasks';
                        hiddenInput.value = firstValue;
                        container.appendChild(hiddenInput);
                    }
                }
            }

            getRows().forEach((row) => {
                const input = getRowInput(row);

                if (input) {
                    input.value = input.value.trim();
                }
            });
        });

        updateRemoveButtons();
    }

    document.querySelectorAll('.todo-subtasks-toggle').forEach((button) => {
        button.addEventListener('click', () => {
            const panelId = button.getAttribute('aria-controls');
            const panel = document.getElementById(panelId);

            if (!panel) {
                return;
            }

            const expanded =
                button.getAttribute('aria-expanded') === 'true';

            button.setAttribute('aria-expanded', String(!expanded));
            panel.hidden = expanded;
        });
    });

    document.addEventListener('submit', async (event) => {
        const form = event.target;

        if (!(form instanceof HTMLFormElement)) {
            return;
        }

        const checkboxButton = form.querySelector('.todo-subtask-checkbox');
        const legacyCheckbox = form.querySelector('.todo-subtask-inline-toggle');

        if (!checkboxButton && !legacyCheckbox) {
            return;
        }

        event.preventDefault();

        if (form.dataset.submitting === 'true') {
            return;
        }

        const csrfToken = getCsrfToken(form);

        if (!csrfToken) {
            console.error('CSRF token not found.');
            return;
        }

        form.dataset.submitting = 'true';

        if (checkboxButton) {
            checkboxButton.disabled = true;
        }

        if (legacyCheckbox) {
            legacyCheckbox.disabled = true;
        }

        try {
            const data = await postAjax(form.action, csrfToken);
            const item = form.closest('.todo-subtask-item');
            const title = item?.querySelector('.todo-subtask-title');

            if (checkboxButton) {
                checkboxButton.classList.toggle(
                    'is-completed',
                    Boolean(data.completed)
                );

                checkboxButton.replaceChildren();

                if (data.completed) {
                    const icon = document.createElement('i');
                    icon.className = 'bi bi-check-lg';
                    icon.setAttribute('aria-hidden', 'true');
                    checkboxButton.appendChild(icon);
                }
            }

            if (legacyCheckbox) {
                legacyCheckbox.checked = Boolean(data.completed);
            }

            title?.classList.toggle(
                'is-completed',
                Boolean(data.completed)
            );
        } catch (error) {
            console.error('Subtask toggle failed:', error);
        } finally {
            delete form.dataset.submitting;

            if (checkboxButton) {
                checkboxButton.disabled = false;
            }

            if (legacyCheckbox) {
                legacyCheckbox.disabled = false;
            }
        }
    });

    document.addEventListener('submit', async (event) => {
        const form = event.target;

        if (
            !(form instanceof HTMLFormElement) ||
            !form.querySelector('.todo-subtask-delete')
        ) {
            return;
        }

        event.preventDefault();

        if (form.dataset.submitting === 'true') {
            return;
        }

        const csrfToken = getCsrfToken(form);
        const item = form.closest('.todo-subtask-item');

        if (!csrfToken || !item) {
            return;
        }

        const list = item.closest('.todo-subtask-list');
        const panel = item.closest('.todo-subtasks-panel');
        const deleteButton = form.querySelector('.todo-subtask-delete');

        form.dataset.submitting = 'true';

        if (deleteButton) {
            deleteButton.disabled = true;
        }

        try {
            await postAjax(form.action, csrfToken);
            item.remove();

            if (list && !list.querySelector('.todo-subtask-item')) {
                const empty = document.createElement('p');
                empty.className = 'todo-subtasks-empty';
                empty.textContent =
                    'No subtasks yet. Add the first step for this task.';
                list.replaceWith(empty);
            }

            if (panel) {
                panel.hidden = false;

                document.querySelector(
                    `.todo-subtasks-toggle[aria-controls="${panel.id}"]`
                )?.setAttribute('aria-expanded', 'true');
            }
        } catch (error) {
            console.error('Subtask deletion failed:', error);

            if (deleteButton) {
                deleteButton.disabled = false;
            }

            delete form.dataset.submitting;
        }
    });

    document.addEventListener('submit', async (event) => {
        const form = event.target;

        if (
            !(form instanceof HTMLFormElement) ||
            !form.matches('.todo-subtask-form')
        ) {
            return;
        }

        event.preventDefault();

        if (form.dataset.submitting === 'true') {
            return;
        }

        const input = form.querySelector('[name="title"]');
        const title = input?.value.trim();

        if (!title) {
            input?.focus();
            return;
        }

        const csrfToken = getCsrfToken(form);
        const panel = form.closest('.todo-subtasks-panel');

        if (!csrfToken || !panel) {
            return;
        }

        const submitButton = form.querySelector('button[type="submit"]');

        form.dataset.submitting = 'true';

        if (submitButton) {
            submitButton.disabled = true;
        }

        try {
            const data = await postAjax(
                form.action,
                csrfToken,
                new FormData(form)
            );

            let list = panel.querySelector('.todo-subtask-list');

            if (!list) {
                list = document.createElement('div');
                list.className = 'todo-subtask-list';

                const empty = panel.querySelector('.todo-subtasks-empty');

                if (empty) {
                    empty.replaceWith(list);
                } else {
                    form.after(list);
                }
            }

            const todoId = panel.id.replace('todo-subtasks-', '');
            const itemId = data.item_id;

            const row = document.createElement('div');
            row.className = 'todo-subtask-item';
            row.dataset.itemId = itemId;

            const dragHandle = document.createElement('button');
            dragHandle.type = 'button';
            dragHandle.className = 'todo-subtask-drag-handle';
            dragHandle.setAttribute('aria-label', 'Reorder subtask');
            dragHandle.title = 'Drag to reorder';
            dragHandle.draggable = true;

            const toggleForm = document.createElement('form');
            toggleForm.method = 'post';
            toggleForm.action =
                `/workspace/todo/${todoId}/items/${itemId}/toggle/`;

            const toggleCsrf = document.createElement('input');
            toggleCsrf.type = 'hidden';
            toggleCsrf.name = 'csrfmiddlewaretoken';
            toggleCsrf.value = csrfToken;

            const checkboxButton = document.createElement('button');
            checkboxButton.type = 'submit';
            checkboxButton.className = 'todo-subtask-checkbox';
            checkboxButton.setAttribute('aria-label', 'Toggle subtask');

            toggleForm.append(toggleCsrf, checkboxButton);

            const titleSpan = document.createElement('span');
            titleSpan.className = 'todo-subtask-title';
            titleSpan.textContent = data.title;

            const deleteForm = document.createElement('form');
            deleteForm.method = 'post';
            deleteForm.action =
                `/workspace/todo/${todoId}/items/${itemId}/delete/`;

            const deleteCsrf = document.createElement('input');
            deleteCsrf.type = 'hidden';
            deleteCsrf.name = 'csrfmiddlewaretoken';
            deleteCsrf.value = csrfToken;

            const deleteButton = document.createElement('button');
            deleteButton.type = 'submit';
            deleteButton.className = 'todo-subtask-delete';
            deleteButton.setAttribute('aria-label', 'Delete subtask');

            const deleteIcon = document.createElement('i');
            deleteIcon.className = 'bi bi-trash3';
            deleteIcon.setAttribute('aria-hidden', 'true');

            deleteButton.appendChild(deleteIcon);
            deleteForm.append(deleteCsrf, deleteButton);

            row.append(
                dragHandle,
                toggleForm,
                titleSpan,
                deleteForm
            );

            list.appendChild(row);

            input.value = '';
            input.focus();

            panel.hidden = false;

            document.querySelector(
                `.todo-subtasks-toggle[aria-controls="${panel.id}"]`
            )?.setAttribute('aria-expanded', 'true');
        } catch (error) {
            console.error('Subtask creation failed:', error);
        } finally {
            delete form.dataset.submitting;

            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });
});
