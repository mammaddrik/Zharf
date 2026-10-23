
document.addEventListener('DOMContentLoaded', () => {

    const builder = document.querySelector('.readme-builder');

    if (!builder) return;

    const navigationItems = builder.querySelectorAll(
        '.readme-builder-nav-item[data-panel]'
    );

    const componentsPanel = builder.querySelector(
        '.readme-components-panel'
    );

    const viewButtons = builder.querySelectorAll(
        '.readme-document-tab[data-view]'
    );

    const viewPanels = builder.querySelectorAll('[data-view-panel]');

    const canvas = builder.querySelector('#readme-document-canvas');
    const previewPanel = builder.querySelector('#readme-preview-content');
    const sourceInput = builder.querySelector('#readme-source-content');

    const blockCount = builder.querySelector('#readme-block-count');
    const characterCount = builder.querySelector(
        '#readme-preview-character-count'
    );

    const projectNameInput = builder.querySelector('#project-name-input');
    const headingSelect = builder.querySelector(
        '[data-field-setting="tag"]'
    );

    const documentTitle = builder.querySelector(
        '.readme-document-title > div > span'
    );

    const projectField = builder.querySelector(
        '.readme-field[data-field-type="project-name"]'
    );

    if (
        !canvas ||
        !previewPanel ||
        !sourceInput ||
        !projectNameInput ||
        !headingSelect
    ) {
        console.error('README Studio: Required elements were not found.');
        return;
    }

    function activateBuilderPanel(selectedPanel) {
        navigationItems.forEach((item) => {
            const isActive = item.dataset.panel === selectedPanel;

            item.classList.toggle('is-active', isActive);
            item.setAttribute('aria-pressed', String(isActive));
        });

        if (componentsPanel) {
            componentsPanel.hidden = selectedPanel !== 'custom';
        }
    }

    navigationItems.forEach((item) => {
        item.addEventListener('click', () => {
            activateBuilderPanel(item.dataset.panel);
        });
    });

    const initialNavigation = builder.querySelector(
        '.readme-builder-nav-item.is-active[data-panel]'
    );

    activateBuilderPanel(initialNavigation?.dataset.panel || 'sections');

    function activateView(selectedView) {
        viewButtons.forEach((button) => {
            const isActive = button.dataset.view === selectedView;

            button.classList.toggle('is-active', isActive);
            button.setAttribute('aria-pressed', String(isActive));
        });

        viewPanels.forEach((panel) => {
            panel.hidden = panel.dataset.viewPanel !== selectedView;
        });

        if (selectedView === 'preview') {
            renderDocument();
        }
    }

    viewButtons.forEach((button) => {
        button.addEventListener('click', () => {
            activateView(button.dataset.view);
        });
    });

    const fieldState = {
        tag: headingSelect.value || 'h1',
        alignment: 'left',
        bold: false,
        italic: false,
        underline: false,
        strikethrough: false
    };

    function getProjectName() {
        return projectNameInput.value.trim();
    }

    function getFormattedText(text) {
        let result = text;

        if (fieldState.bold) {
            result = `**${result}**`;
        }

        if (fieldState.italic) {
            result = `*${result}*`;
        }

        if (fieldState.strikethrough) {
            result = `~~${result}~~`;
        }

        if (fieldState.underline) {
            result = `<u>${result}</u>`;
        }

        return result;
    }

    function escapeHtml(text) {
        return text.replace(/[&<>"']/g, (character) => {
            const entities = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            };

            return entities[character];
        });
    }

    function escapeMarkdown(text) {
        return text.replace(/([\\`*_{}[\]()#+\-.!|>])/g, '\\$1');
    }


    function getMarkdown() {
        const name = getProjectName();

        if (!name) return '';

        // Escape the text before applying formatting.
        let textContent = escapeMarkdown(name);

        if (fieldState.bold) {
            textContent = `**${textContent}**`;
        }

        if (fieldState.italic) {
            textContent = `*${textContent}*`;
        }

        if (fieldState.strikethrough) {
            textContent = `~~${textContent}~~`;
        }

        if (fieldState.underline) {
            textContent = `<ins>${textContent}</ins>`;
        }

        let content;

        if (fieldState.tag === 'p') {
            content = textContent;
        } else {
            const level = Number(fieldState.tag.slice(1));
            content = `${'#'.repeat(level)} ${textContent}`;
        }

        if (fieldState.alignment !== 'left') {
            content =
                `<div align="${fieldState.alignment}">\n\n` +
                `${content}\n\n` +
                `</div>`;
        }

        return content;
    }

    function renderDocument() {
        const name = getProjectName();
        const markdown = getMarkdown();

        previewPanel.replaceChildren();

        if (!name) {
            const emptyState = document.createElement('div');
            emptyState.className = 'readme-document-empty';

            const iconWrapper = document.createElement('span');
            iconWrapper.className = 'readme-document-empty-icon';

            const icon = document.createElement('i');
            icon.className = 'bi bi-eye';
            icon.setAttribute('aria-hidden', 'true');

            const title = document.createElement('h3');
            title.textContent = 'Preview will appear here';

            const description = document.createElement('p');
            description.textContent =
                'Your README preview will be displayed here without editing controls.';

            iconWrapper.append(icon);
            emptyState.append(iconWrapper, title, description);
            previewPanel.append(emptyState);
        } else {
            const element = document.createElement(fieldState.tag);
            element.textContent = name;
            element.style.textAlign = fieldState.alignment;

            if (fieldState.bold) {
                element.style.fontWeight = '700';
            }

            if (fieldState.italic) {
                element.style.fontStyle = 'italic';
            }

            const decorations = [];

            if (fieldState.underline) {
                decorations.push('underline');
            }

            if (fieldState.strikethrough) {
                decorations.push('line-through');
            }

            if (decorations.length) {
                element.style.textDecoration = decorations.join(' ');
            }

            previewPanel.append(element);
        }

        sourceInput.value = markdown;

        if (blockCount) {
            blockCount.textContent = name ? '1 block' : '0 blocks';
        }

        if (characterCount) {
            characterCount.textContent =
                `${name.length} ${name.length === 1 ? 'character' : 'characters'}`;
        }

        if (documentTitle) {
            documentTitle.textContent = name
                ? `${name}.md`
                : 'Untitled README.md';
        }
    }

    projectNameInput.addEventListener('input', renderDocument);

    headingSelect.addEventListener('change', () => {
        const allowedTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'];

        fieldState.tag = allowedTags.includes(headingSelect.value)
            ? headingSelect.value
            : 'h1';

        renderDocument();
    });

    const alignmentButtons = builder.querySelectorAll(
        '[data-field-setting="alignment"][data-value]'
    );

    alignmentButtons.forEach((button) => {
        button.addEventListener('click', () => {
            fieldState.alignment = button.dataset.value;

            alignmentButtons.forEach((item) => {
                const isActive = item === button;

                item.classList.toggle('is-active', isActive);
                item.setAttribute('aria-pressed', String(isActive));
            });

            renderDocument();
        });
    });

    const styleButtons = builder.querySelectorAll(
        '[data-field-setting="bold"], ' +
        '[data-field-setting="italic"], ' +
        '[data-field-setting="underline"], ' +
        '[data-field-setting="strikethrough"]'
    );

    styleButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const setting = button.dataset.fieldSetting;

            fieldState[setting] = !fieldState[setting];

            button.classList.toggle('is-active', fieldState[setting]);
            button.setAttribute(
                'aria-pressed',
                String(fieldState[setting])
            );

            renderDocument();
        });
    });

    const fieldActionButtons = builder.querySelectorAll(
        '.readme-field-action[data-action]'
    );

    fieldActionButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (!projectField) return;

            const action = button.dataset.action;

            if (action === 'clear') {
                projectNameInput.value = '';
                renderDocument();
                projectNameInput.focus();
                return;
            }

            if (action === 'move-up' || action === 'move-down') {
                const fields = Array.from(
                    canvas.querySelectorAll('.readme-field')
                );

                const currentIndex = fields.indexOf(projectField);

                if (currentIndex === -1) return;

                if (action === 'move-up' && currentIndex > 0) {
                    canvas.insertBefore(
                        projectField,
                        fields[currentIndex - 1]
                    );
                }

                if (
                    action === 'move-down' &&
                    currentIndex < fields.length - 1
                ) {
                    const nextField = fields[currentIndex + 1];

                    canvas.insertBefore(
                        nextField,
                        projectField
                    );
                }
            }
        });
    });

    const componentButtons = builder.querySelectorAll(
        '.readme-component-item[data-component]'
    );

    componentButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const component = button.dataset.component;

            if (component === 'project-name') {
                activateView('edit');
                projectNameInput.focus();
                projectNameInput.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }
        });
    });

    renderDocument();
    activateView('edit');
});
