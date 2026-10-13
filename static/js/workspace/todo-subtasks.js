document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('todo-subtask-inputs');
    const addButton = document.getElementById('todo-add-subtask-input');
    const firstInput = document.getElementById('todo-subtask-first-input');
    const todoForm = addButton?.closest('form');

    if (container && addButton && firstInput && todoForm) {
        let draggedRow = null;

        const getRows = () => [
            ...container.querySelectorAll('.todo-subtask-input-row')
        ];

        const updateRemoveButtons = () => {
            const rows = getRows();
            const showDragHandles = rows.length > 1;

            rows.forEach((row) => {
                const removeButton = row.querySelector('.todo-subtask-remove');
                const dragHandle = row.querySelector('.todo-subtask-drag-handle');

                if (dragHandle) {
                    dragHandle.hidden = !showDragHandles;
                    dragHandle.style.display = showDragHandles
                        ? 'inline-flex'
                        : 'none';
                }

                if (removeButton) {
                    removeButton.hidden = rows.length <= 1;
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
            removeButton.innerHTML =
                '<i class="bi bi-trash3" aria-hidden="true"></i>';

            row.append(handle, input, removeButton);

            return row;
        };

        addButton.addEventListener('click', () => {
            const value = firstInput.value.trim();

            container.appendChild(createSubtaskRow(value));
            firstInput.value = '';

            updateRemoveButtons();
        });

        firstInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault();
                addButton.click();
            }
        });

        container.addEventListener('click', (event) => {
            const removeButton = event.target.closest('.todo-subtask-remove');

            if (!removeButton) {
                return;
            }

            const row = removeButton.closest('.todo-subtask-input-row');

            if (row) {
                row.remove();
                updateRemoveButtons();
            }
        });

        container.addEventListener('dragstart', (event) => {
            const handle = event.target.closest('.todo-subtask-drag-handle');

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

            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', 'subtask');
        });

        container.addEventListener('dragover', (event) => {
            if (!draggedRow) {
                return;
            }

            event.preventDefault();

            const targetRow = event.target.closest('.todo-subtask-input-row');

            if (!targetRow || targetRow === draggedRow) {
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
            const firstValue = firstInput.value.trim();

            if (firstValue) {
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'subtasks';
                hiddenInput.value = firstValue;
                todoForm.appendChild(hiddenInput);
            }

            getRows().forEach((row) => {
                const input = row.querySelector('input[name="subtasks"]');

                if (input) {
                    input.value = input.value.trim();
                }
            });
        });

        updateRemoveButtons();
    }

    document.querySelectorAll('.todo-subtask-inline-toggle').forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            const form = document.createElement('form');
            form.method = 'post';
            form.action = checkbox.dataset.toggleUrl;

            const csrfToken = document.querySelector(
                '[name="csrfmiddlewaretoken"]'
            );

            if (!csrfToken) {
                checkbox.checked = !checkbox.checked;
                return;
            }

            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken.value;

            form.appendChild(csrfInput);
            document.body.appendChild(form);
            form.submit();
        });
    });

    document.querySelectorAll('.todo-subtask-delete').forEach((button) => {
        button.addEventListener('click', () => {
            const form = document.createElement('form');
            form.method = 'post';
            form.action = button.dataset.deleteUrl;

            const csrfToken = document.querySelector(
                '[name="csrfmiddlewaretoken"]'
            );

            if (!csrfToken) {
                return;
            }

            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken.value;

            form.appendChild(csrfInput);
            document.body.appendChild(form);
            form.submit();
        });
    });

    document.querySelectorAll('.todo-subtasks-toggle').forEach((button) => {
        button.addEventListener('click', () => {
            const panelId = button.getAttribute('aria-controls');
            const panel = document.getElementById(panelId);

            if (!panel) {
                return;
            }

            const isExpanded =
                button.getAttribute('aria-expanded') === 'true';

            button.setAttribute('aria-expanded', String(!isExpanded));
            panel.hidden = isExpanded;
        });
    });
});
