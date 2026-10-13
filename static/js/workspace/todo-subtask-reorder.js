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

        const getItems = () => [
            ...list.querySelectorAll('.todo-subtask-item')
        ];

        getItems().forEach((item) => {
            const handle = item.querySelector('.todo-subtask-drag-handle');

            if (!handle) {
                return;
            }

            handle.draggable = true;

            handle.addEventListener('dragstart', (event) => {
                draggedItem = item;
                originalOrder = getItems();

                item.classList.add('is-dragging');

                event.dataTransfer.effectAllowed = 'move';
                event.dataTransfer.setData('text/plain', item.dataset.itemId);
            });

            item.addEventListener('dragover', (event) => {
                event.preventDefault();

                if (!draggedItem || draggedItem === item) {
                    return;
                }

                const rect = item.getBoundingClientRect();
                const insertAfter = event.clientY > rect.top + rect.height / 2;

                if (insertAfter) {
                    item.after(draggedItem);
                } else {
                    item.before(draggedItem);
                }
            });

            item.addEventListener('drop', (event) => {
                event.preventDefault();
            });

            handle.addEventListener('dragend', async () => {
                if (!draggedItem) {
                    return;
                }

                draggedItem.classList.remove('is-dragging');
                draggedItem = null;

                const newOrder = getItems();

                const orderChanged = newOrder.some(
                    (item, index) => item !== originalOrder[index]
                );

                if (!orderChanged) {
                    return;
                }

                const saved = await saveOrder(list, newOrder);

                if (!saved) {
                    originalOrder.forEach((item) => {
                        list.appendChild(item);
                    });
                }
            });
        });
    });

    async function saveOrder(list, items) {
        const csrfToken = getCookie('csrftoken');

        if (!csrfToken) {
            console.error('CSRF token not found.');
            return false;
        }

        const body = new URLSearchParams();

        items.forEach((item) => {
            body.append('item_ids[]', item.dataset.itemId);
        });

        try {
            const response = await fetch(list.dataset.reorderUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
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
            console.error('Error saving subtask order:', error);
            return false;
        }
    }
});
