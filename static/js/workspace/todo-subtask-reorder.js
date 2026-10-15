document.addEventListener('DOMContentLoaded', () => {
    const lists = document.querySelectorAll('.todo-subtask-list');

    const getCookie = (name) => {
        const cookies = document.cookie.split(';');

        for (const cookie of cookies) {
            const trimmedCookie = cookie.trim();

            if (trimmedCookie.startsWith(`${name}=`)) {
                return decodeURIComponent(
                    trimmedCookie.substring(name.length + 1)
                );
            }
        }

        return null;
    };

    lists.forEach((list) => {
        let draggedItem = null;
        let originalOrder = [];
        let savingOrder = false;

        const getItems = () => [
            ...list.querySelectorAll('.todo-subtask-item')
        ];

        getItems().forEach((item) => {
            const handle = item.querySelector(
                '.todo-subtask-drag-handle'
            );

            if (!handle) {
                return;
            }

            handle.draggable = true;

            handle.addEventListener('dragstart', (event) => {
                if (savingOrder) {
                    event.preventDefault();
                    return;
                }

                draggedItem = item;
                originalOrder = getItems();

                item.classList.add('is-dragging');

                if (event.dataTransfer) {
                    event.dataTransfer.effectAllowed = 'move';
                    event.dataTransfer.setData(
                        'text/plain',
                        item.dataset.itemId || ''
                    );
                }
            });

            item.addEventListener('dragover', (event) => {
                if (!draggedItem || draggedItem === item) {
                    return;
                }

                event.preventDefault();

                const rect = item.getBoundingClientRect();
                const insertAfter =
                    event.clientY > rect.top + rect.height / 2;

                if (insertAfter) {
                    item.after(draggedItem);
                } else {
                    item.before(draggedItem);
                }
            });

            item.addEventListener('drop', (event) => {
                if (draggedItem) {
                    event.preventDefault();
                }
            });

            handle.addEventListener('dragend', async () => {
                if (!draggedItem) {
                    return;
                }

                const itemBeingDragged = draggedItem;

                itemBeingDragged.classList.remove('is-dragging');
                draggedItem = null;

                const newOrder = getItems();

                const orderChanged = newOrder.some(
                    (currentItem, index) =>
                        currentItem !== originalOrder[index]
                );

                if (!orderChanged) {
                    return;
                }

                savingOrder = true;

                try {
                    const saved = await saveOrder(list, newOrder);

                    if (!saved) {
                        originalOrder.forEach((originalItem) => {
                            list.appendChild(originalItem);
                        });
                    }
                } finally {
                    savingOrder = false;
                }
            });
        });
    });

    async function saveOrder(list, items) {
        const csrfToken = getCookie('csrftoken');
        const reorderUrl = list.dataset.reorderUrl;

        if (!csrfToken) {
            console.error('CSRF token not found.');
            return false;
        }

        if (!reorderUrl) {
            console.error('Subtask reorder URL not found.');
            return false;
        }

        const body = new URLSearchParams();

        items.forEach((item) => {
            if (!item.dataset.itemId) {
                console.error(
                    'Subtask is missing data-item-id:',
                    item
                );
                return;
            }

            body.append('item_ids[]', item.dataset.itemId);
        });

        try {
            const response = await fetch(reorderUrl, {
                method: 'POST',
                headers: {
                    'Content-Type':
                        'application/x-www-form-urlencoded;charset=UTF-8',
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: body.toString(),
                credentials: 'same-origin'
            });

            if (!response.ok) {
                console.error(
                    'Failed to save subtask order:',
                    response.status,
                    await response.text()
                );

                return false;
            }

            return true;
        } catch (error) {
            console.error(
                'Error saving subtask order:',
                error
            );

            return false;
        }
    }
});
