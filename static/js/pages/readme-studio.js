
document.addEventListener('DOMContentLoaded', () => {
    const builder = document.querySelector('.readme-builder');

    if (!builder) return;

    // --------------------------------------------------
    // Elements
    // --------------------------------------------------

    const navigationItems = builder.querySelectorAll(
        '.readme-builder-nav-item[data-panel]'
    );

    const componentsPanel = builder.querySelector('.readme-components-panel');

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

    const documentTitle = builder.querySelector(
        '.readme-document-title > div > span'
    );

    const projectNameInput = builder.querySelector('#project-name-input');
    const headingSelect = builder.querySelector(
        '[data-field-setting="tag"]'
    );

    const projectField = builder.querySelector(
        '.readme-field[data-field-type="project-name"]'
    );

    const bannerField = builder.querySelector(
        '.readme-field[data-field-type="banner"]'
    );

    if (!canvas || !previewPanel || !sourceInput) {
        console.error('README Studio: Required document elements were not found.');
        return;
    }

    // --------------------------------------------------
    // State
    // --------------------------------------------------

    const textState = {
        tag: headingSelect?.value || 'h1',
        alignment: 'left',
        bold: false,
        italic: false,
        underline: false,
        strikethrough: false
    };

    const bannerState = {
        alignment: 'left'
    };

    const bannerInputs = {
        url: builder.querySelector('[data-field-input="banner-url"]'),
        alt: builder.querySelector('[data-field-input="banner-alt"]'),
        width: builder.querySelector('[data-field-input="banner-width"]'),
        height: builder.querySelector('[data-field-input="banner-height"]'),
        link: builder.querySelector('[data-field-input="banner-link"]')
    };

    // --------------------------------------------------
    // Navigation
    // --------------------------------------------------

    function activateBuilderPanel(selectedPanel) {
        navigationItems.forEach((item) => {
            const active = item.dataset.panel === selectedPanel;

            item.classList.toggle('is-active', active);
            item.setAttribute('aria-pressed', String(active));
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

    // --------------------------------------------------
    // Document views
    // --------------------------------------------------

    function activateView(selectedView) {
        viewButtons.forEach((button) => {
            const active = button.dataset.view === selectedView;

            button.classList.toggle('is-active', active);
            button.setAttribute('aria-pressed', String(active));
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

    // --------------------------------------------------
    // Helpers
    // --------------------------------------------------

    function escapeHtml(value) {
        return String(value ?? '').replace(/[&<>"']/g, (character) => {
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

    function escapeMarkdown(value) {
        return String(value ?? '').replace(
            /([\\`*_{}\[\]()#+\-.!|>])/g,
            '\\$1'
        );
    }

    function getSafeDimension(value) {
        const dimension = String(value ?? '').trim();

        if (!dimension) return '';

        // Allow positive pixel values, percentages, and common CSS units.
        if (!/^\d+(?:\.\d+)?(?:px|%|em|rem|vw|vh)?$/i.test(dimension)) {
            return '';
        }

        const number = Number.parseFloat(dimension);

        if (!Number.isFinite(number) || number <= 0) {
            return '';
        }

        return /^\d+(?:\.\d+)?$/.test(dimension)
            ? `${dimension}px`
            : dimension;
    }

    function getProjectName() {
        return projectNameInput?.value.trim() || '';
    }

    function getBannerData() {
        return {
            url: getSafeUrl(bannerInputs.url?.value),
            alt: bannerInputs.alt?.value.trim() || '',
            width: getSafeDimension(bannerInputs.width?.value),
            height: getSafeDimension(bannerInputs.height?.value),
            link: getSafeUrl(bannerInputs.link?.value),
            alignment: bannerState.alignment
        };
    }

    function hasBannerContent() {
        return Boolean(bannerInputs.url?.value.trim());
    }

    function getFields() {
        return Array.from(canvas.querySelectorAll('.readme-field'));
    }

    function isFieldPopulated(field) {
        if (field.dataset.fieldType === 'project-name') {
            return Boolean(getProjectName());
        }

        if (field.dataset.fieldType === 'banner') {
            return hasBannerContent();
        }

        return false;
    }

    // --------------------------------------------------
    // Text Markdown
    // --------------------------------------------------

    function getTextMarkdown() {
        const name = getProjectName();

        if (!name) return '';

        let content = escapeMarkdown(name);

        if (textState.bold) {
            content = `**${content}**`;
        }

        if (textState.italic) {
            content = `*${content}*`;
        }

        if (textState.strikethrough) {
            content = `~~${content}~~`;
        }

        if (textState.underline) {
            content = `<ins>${content}</ins>`;
        }

        if (textState.tag !== 'p') {
            const level = Number(textState.tag.slice(1));
            content = `${'#'.repeat(level)} ${content}`;
        }

        if (textState.alignment !== 'left') {
            content =
                `<div align="${textState.alignment}">\n\n` +
                `${content}\n\n` +
                '</div>';
        }

        return content;
    }

    // --------------------------------------------------
    // Banner Markdown
    // --------------------------------------------------

    function getBannerMarkdown() {
        const banner = getBannerData();

        if (!banner.url) return '';

        const attributes = [
            `src="${escapeHtml(banner.url)}"`,
            `alt="${escapeHtml(banner.alt)}"`
        ];

        if (banner.width) {
            attributes.push(`width="${escapeHtml(banner.width)}"`);
        }

        if (banner.height) {
            attributes.push(`height="${escapeHtml(banner.height)}"`);
        }

        const image = `<img ${attributes.join(' ')} />`;

        const linkedImage = banner.link
            ? `<a href="${escapeHtml(banner.link)}">${image}</a>`
            : image;

        return (
            `<div align="${banner.alignment}">\n\n` +
            `${linkedImage}\n\n` +
            '</div>'
        );
    }

    // --------------------------------------------------
    // Preview rendering
    // --------------------------------------------------

    function renderEmptyPreview() {
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
    }

    function renderTextPreview() {
        const name = getProjectName();

        if (!name) return;

        const allowedTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'];
        const tag = allowedTags.includes(textState.tag)
            ? textState.tag
            : 'h1';

        const element = document.createElement(tag);
        element.textContent = name;
        element.style.textAlign = textState.alignment;

        if (textState.bold) {
            element.style.fontWeight = '700';
        }

        if (textState.italic) {
            element.style.fontStyle = 'italic';
        }

        const decorations = [];

        if (textState.underline) {
            decorations.push('underline');
        }

        if (textState.strikethrough) {
            decorations.push('line-through');
        }

        if (decorations.length) {
            element.style.textDecoration = decorations.join(' ');
        }

        previewPanel.append(element);
    }

    function renderBannerPreview() {
        const banner = getBannerData();

        if (!banner.url) return;

        const wrapper = document.createElement('div');
        wrapper.className = `readme-banner-preview align-${banner.alignment}`;

        const image = document.createElement('img');
        image.src = banner.url;
        image.alt = banner.alt;
        image.loading = 'lazy';

        if (banner.width) {
            image.style.width = banner.width;
        }

        if (banner.height) {
            image.style.height = banner.height;
        }

        image.style.maxWidth = '100%';

        if (banner.height) {
            image.style.objectFit = 'contain';
        }

        image.addEventListener('error', () => {
            wrapper.remove();
        }, { once: true });

        if (banner.link) {
            const link = document.createElement('a');
            link.href = banner.link;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.setAttribute('aria-label', banner.alt || 'Open banner link');

            link.append(image);
            wrapper.append(link);
        } else {
            wrapper.append(image);
        }

        previewPanel.append(wrapper);
    }

    // --------------------------------------------------
    // Build document Markdown in canvas order
    // --------------------------------------------------

    function getDocumentMarkdown() {
        return getFields()
            .map((field) => {
                if (field.dataset.fieldType === 'project-name') {
                    return getTextMarkdown();
                }

                if (field.dataset.fieldType === 'banner') {
                    return getBannerMarkdown();
                }

                return '';
            })
            .filter(Boolean)
            .join('\n\n');
    }

    // --------------------------------------------------
    // Render complete document
    // --------------------------------------------------

    function renderDocument() {
        previewPanel.replaceChildren();

        const fields = getFields();
        const populatedFields = fields.filter(isFieldPopulated);

        if (populatedFields.length === 0) {
            renderEmptyPreview();
        } else {
            populatedFields.forEach((field) => {
                if (field.dataset.fieldType === 'project-name') {
                    renderTextPreview();
                }

                if (field.dataset.fieldType === 'banner') {
                    renderBannerPreview();
                }
            });
        }

        const markdown = getDocumentMarkdown();
        sourceInput.value = markdown;

        if (blockCount) {
            const count = populatedFields.length;
            blockCount.textContent =
                `${count} ${count === 1 ? 'block' : 'blocks'}`;
        }

        if (characterCount) {
            const count = markdown.length;

            characterCount.textContent =
                `${count} ${count === 1 ? 'character' : 'characters'}`;
        }

        if (documentTitle) {
            const name = getProjectName();

            documentTitle.textContent = name
                ? `${name}.md`
                : 'Untitled README.md';
        }
    }

    // --------------------------------------------------
    // Text events
    // --------------------------------------------------

    if (projectNameInput) {
        projectNameInput.addEventListener('input', renderDocument);
    }

    if (headingSelect) {
        headingSelect.addEventListener('change', () => {
            const allowedTags = [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'
            ];

            textState.tag = allowedTags.includes(headingSelect.value)
                ? headingSelect.value
                : 'h1';

            renderDocument();
        });
    }

    const alignmentButtons = builder.querySelectorAll(
        '[data-field-setting="alignment"][data-value]'
    );

    alignmentButtons.forEach((button) => {
        button.addEventListener('click', () => {
            textState.alignment = button.dataset.value;

            alignmentButtons.forEach((item) => {
                const active = item === button;

                item.classList.toggle('is-active', active);
                item.setAttribute('aria-pressed', String(active));
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

            textState[setting] = !textState[setting];

            button.classList.toggle('is-active', textState[setting]);
            button.setAttribute(
                'aria-pressed',
                String(textState[setting])
            );

            renderDocument();
        });
    });

    // --------------------------------------------------
    // Banner events
    // --------------------------------------------------

    Object.values(bannerInputs).forEach((input) => {
        if (!input) return;

        input.addEventListener('input', renderDocument);
        input.addEventListener('change', renderDocument);
    });

    const bannerAlignmentButtons = builder.querySelectorAll(
        '[data-banner-setting="alignment"][data-value]'
    );

    bannerAlignmentButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const alignment = button.dataset.value;

            if (!['left', 'center', 'right'].includes(alignment)) {
                return;
            }

            bannerState.alignment = alignment;

            bannerAlignmentButtons.forEach((item) => {
                const active = item === button;

                item.classList.toggle('is-active', active);
                item.setAttribute('aria-pressed', String(active));
            });

            renderDocument();
        });
    });

    // --------------------------------------------------
    // Clear and reorder any component
    // --------------------------------------------------

    const fieldActionButtons = builder.querySelectorAll(
        '.readme-field-action[data-action]'
    );

    fieldActionButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const field = button.closest('.readme-field');

            if (!field || !canvas.contains(field)) return;

            const action = button.dataset.action;
            const fieldType = field.dataset.fieldType;

            if (action === 'clear') {
                if (fieldType === 'project-name' && projectNameInput) {
                    projectNameInput.value = '';
                }

                if (fieldType === 'banner') {
                    Object.values(bannerInputs).forEach((input) => {
                        if (input) input.value = '';
                    });

                    bannerState.alignment = 'left';

                    bannerAlignmentButtons.forEach((item) => {
                        const active = item.dataset.value === 'left';

                        item.classList.toggle('is-active', active);
                        item.setAttribute('aria-pressed', String(active));
                    });
                }

                renderDocument();

                const firstInput = field.querySelector(
                    '[data-field-input]'
                );

                firstInput?.focus();
                return;
            }

            const fields = getFields();
            const index = fields.indexOf(field);

            if (index === -1) return;

            if (action === 'move-up' && index > 0) {
                canvas.insertBefore(field, fields[index - 1]);
                renderDocument();
            }

            if (action === 'move-down' && index < fields.length - 1) {
                const nextField = fields[index + 1];

                canvas.insertBefore(nextField, field);
                renderDocument();
            }
        });
    });

    // --------------------------------------------------
    // Component navigation
    // --------------------------------------------------

    const componentButtons = builder.querySelectorAll(
        '.readme-component-item[data-component]'
    );

    componentButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const component = button.dataset.component;

            const field = canvas.querySelector(
                `.readme-field[data-field-type="${component}"]`
            );

            if (!field) return;

            activateView('edit');

            const input = field.querySelector('[data-field-input]');

            field.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });

            input?.focus({ preventScroll: true });
        });
    });

    // --------------------------------------------------
    // Initial render
    // --------------------------------------------------

    renderDocument();
    activateView('edit');
});
