const collectionTree = document.querySelector(
    '.documents-collection-tree'
);

if (collectionTree) {
    const items = Array.from(
        collectionTree.querySelectorAll(
            '.documents-collection-item'
        )
    );

    const getDepth = function (item) {
        return Number(
            item.dataset.collectionDepth
        );
    };

    const getDirectChildren = function (itemIndex) {
        const children = [];
        const parentDepth = getDepth(
            items[itemIndex]
        );

        for (
            let index = itemIndex + 1;
            index < items.length;
            index++
        ) {
            const depth = getDepth(items[index]);

            if (depth <= parentDepth) {
                break;
            }

            if (depth === parentDepth + 1) {
                children.push(index);
            }
        }

        return children;
    };

    const setChildrenVisibility = function (
        itemIndex,
        visible
    ) {
        const children = getDirectChildren(
            itemIndex
        );

        children.forEach(function (childIndex) {
            const child = items[childIndex];

            child.classList.toggle(
                'is-hidden',
                !visible
            );

            if (!visible) {
                const childToggle =
                    child.querySelector(
                        '.documents-collection-toggle'
                    );

                if (childToggle) {
                    childToggle.setAttribute(
                        'aria-expanded',
                        'false'
                    );
                }

                setChildrenVisibility(
                    childIndex,
                    false
                );
            }
        });
    };

    items.forEach(function (item, index) {
        const toggle = item.querySelector(
            '.documents-collection-toggle'
        );

        if (!toggle) {
            return;
        }

        toggle.addEventListener(
            'click',
            function (event) {
                event.preventDefault();
                event.stopPropagation();

                const isExpanded =
                    toggle.getAttribute(
                        'aria-expanded'
                    ) === 'true';

                toggle.setAttribute(
                    'aria-expanded',
                    String(!isExpanded)
                );

                setChildrenVisibility(
                    index,
                    !isExpanded
                );
            }
        );
    });
}