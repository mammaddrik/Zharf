document.addEventListener('DOMContentLoaded', () => {
    const builder = document.querySelector('.readme-builder');

    if (!builder) return;

    // --------------------------------------------------
    // Elements
    // --------------------------------------------------

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

    const documentTitle = builder.querySelector(
        '.readme-document-title > div > span'
    );

    const projectNameInput = builder.querySelector('#project-name-input');

    const headingSelect = builder.querySelector(
        '[data-field-setting="tag"]'
    );

    const descriptionInput = builder.querySelector(
        '#project-description-input'
    );

    const bannerInputs = {
        url: builder.querySelector('[data-field-input="banner-url"]'),
        alt: builder.querySelector('[data-field-input="banner-alt"]'),
        width: builder.querySelector('[data-field-input="banner-width"]'),
        height: builder.querySelector('[data-field-input="banner-height"]'),
        link: builder.querySelector('[data-field-input="banner-link"]')
    };

    const projectField = builder.querySelector(
        '.readme-field[data-field-type="project-name"]'
    );

    const bannerField = builder.querySelector(
        '.readme-field[data-field-type="banner"]'
    );

    const descriptionField = builder.querySelector(
        '.readme-field[data-field-type="description"]'
    );

    const linkModal = document.getElementById('readme-link-modal');

    const linkModalForm = document.getElementById(
        'readme-link-modal-form'
    );

    const linkUrlInput = document.getElementById(
        'readme-link-url-input'
    );

    const linkSelectedText = document.getElementById(
        'readme-link-selected-text'
    );

    const linkUrlError = document.getElementById(
        'readme-link-url-error'
    );

    const linkCloseButtons = document.querySelectorAll(
        '[data-link-modal-close]'
    );

    if (!canvas || !previewPanel || !sourceInput) {
        console.error(
            'README Studio: Required document elements were not found.'
        );
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

    const descriptionState = {
        alignment: 'left'
    };

    // Stores the selected text and its original position
    // while the link modal is open.
    let pendingLinkSelection = null;

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
    // Document Views
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

    function getSafeUrl(value) {
        const input = String(value ?? '').trim();

        if (!input) return '';

        try {
            const url = new URL(input);

            if (!['http:', 'https:'].includes(url.protocol)) {
                return '';
            }

            return url.href;
        } catch {
            return '';
        }
    }

    function getSafeDimension(value) {
        const dimension = String(value ?? '').trim();

        if (!dimension) return '';

        if (
            !/^\d+(?:\.\d+)?(?:px|%|em|rem|vw|vh)?$/i.test(dimension)
        ) {
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

    function getDescription() {
        return descriptionInput?.value.trim() || '';
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
        return Boolean(getBannerData().url);
    }

    function getFields() {
        return Array.from(canvas.querySelectorAll('.readme-field'));
    }

    function isFieldPopulated(field) {
        switch (field.dataset.fieldType) {
            case 'project-name':
                return Boolean(getProjectName());

            case 'banner':
                return hasBannerContent();

            case 'description':
                return Boolean(getDescription());

            default:
                return false;
        }
    }

    function getAlignment(value) {
        return ['left', 'center', 'right'].includes(value)
            ? value
            : 'left';
    }

    // --------------------------------------------------
    // Add Link Modal
    // --------------------------------------------------

    function isLinkModalOpen() {
        return Boolean(linkModal && !linkModal.hidden);
    }

    function clearLinkModalError() {
        if (linkUrlError) {
            linkUrlError.textContent = '';
            linkUrlError.hidden = true;
        }

        if (linkUrlInput) {
            linkUrlInput.removeAttribute('aria-invalid');
        }
    }

    function showLinkModalError(message) {
        if (!linkUrlError || !linkUrlInput) return;

        linkUrlError.textContent = message;
        linkUrlError.hidden = false;

        linkUrlInput.setAttribute('aria-invalid', 'true');
        linkUrlInput.focus();
    }

    function openLinkModal(start, end, selectedText) {
        if (
            !linkModal ||
            !linkModalForm ||
            !linkUrlInput ||
            !linkSelectedText
        ) {
            console.error(
                'README Studio: Link modal elements were not found.'
            );
            return;
        }

        pendingLinkSelection = {
            start,
            end,
            selectedText
        };

        clearLinkModalError();

        linkModalForm.reset();

        // Set a useful example without requiring the user to remove it.
        linkUrlInput.value = 'https://example.com';

        // Display the selected text safely.
        linkSelectedText.textContent = selectedText;

        linkModal.hidden = false;
        linkModal.setAttribute('aria-hidden', 'false');
        linkModal.classList.add('is-open');

        requestAnimationFrame(() => {
            linkUrlInput.focus();
            linkUrlInput.select();
        });
    }

    function closeLinkModal() {
        if (!linkModal) return;

        linkModal.hidden = true;
        linkModal.setAttribute('aria-hidden', 'true');
        linkModal.classList.remove('is-open');

        clearLinkModalError();

        pendingLinkSelection = null;

        if (descriptionInput) {
            descriptionInput.focus();
        }
    }

    // Close buttons and backdrop.
    linkCloseButtons.forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            closeLinkModal();
        });
    });

    if (linkModal) {
        linkModal.addEventListener('click', (event) => {
            if (
                event.target instanceof Element &&
                event.target.matches('[data-link-modal-close]')
            ) {
                closeLinkModal();
            }
        });
    }

    // Clear validation errors when the URL changes.
    if (linkUrlInput) {
        linkUrlInput.addEventListener('input', clearLinkModalError);
    }

    // Validate and insert the Markdown link.
    if (linkModalForm) {
        linkModalForm.addEventListener('submit', (event) => {
            event.preventDefault();

            if (
                !descriptionInput ||
                !pendingLinkSelection ||
                !linkUrlInput
            ) {
                closeLinkModal();
                return;
            }

            const safeUrl = getSafeUrl(linkUrlInput.value);

            if (!safeUrl) {
                showLinkModalError(
                    'Please enter a valid absolute HTTP or HTTPS URL.'
                );
                return;
            }

            const {
                start,
                end,
                selectedText
            } = pendingLinkSelection;

            const replacement = `[${selectedText}](${safeUrl})`;

            // Insert the Markdown link at the original selection.
            descriptionInput.setRangeText(
                replacement,
                start,
                end,
                'select'
            );

            // Close the modal and return focus to the description editor.
            closeLinkModal();

            // Select only the link text, not the Markdown syntax.
            const selectionStart = start + 1;
            const selectionEnd = selectionStart + selectedText.length;

            descriptionInput.setSelectionRange(
                selectionStart,
                selectionEnd
            );

            renderDocument();
        });
    }

    // Close the modal with Escape.
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && isLinkModalOpen()) {
            event.preventDefault();
            closeLinkModal();
        }
    });

    // --------------------------------------------------
    // Project Name Markdown
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

        const allowedTags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'
        ];

        const tag = allowedTags.includes(textState.tag)
            ? textState.tag
            : 'h1';

        if (tag !== 'p') {
            const level = Number(tag.slice(1));
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
            attributes.push(
                `width="${escapeHtml(banner.width)}"`
            );
        }

        if (banner.height) {
            attributes.push(
                `height="${escapeHtml(banner.height)}"`
            );
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
    // Description Markdown
    // --------------------------------------------------

    function getDescriptionMarkdown() {
        const description = getDescription();

        if (!description) return '';

        if (descriptionState.alignment === 'left') {
            return description;
        }

        return (
            `<div align="${descriptionState.alignment}">\n\n` +
            `${description}\n\n` +
            '</div>'
        );
    }

    // --------------------------------------------------
    // Preview: Empty State
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

    // --------------------------------------------------
    // Preview: Project Name
    // --------------------------------------------------

    function renderTextPreview() {
        const name = getProjectName();

        if (!name) return;

        const allowedTags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'
        ];

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

    // --------------------------------------------------
    // Preview: Banner
    // --------------------------------------------------

    function renderBannerPreview() {
        const banner = getBannerData();

        if (!banner.url) return;

        const wrapper = document.createElement('div');

        wrapper.className =
            `readme-banner-preview align-${banner.alignment}`;

        const image = document.createElement('img');

        image.src = banner.url;
        image.alt = banner.alt;
        image.loading = 'lazy';
        image.style.maxWidth = '100%';

        if (banner.width) {
            image.style.width = banner.width;
        }

        if (banner.height) {
            image.style.height = banner.height;
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
            link.setAttribute(
                'aria-label',
                banner.alt || 'Open banner link'
            );

            link.append(image);
            wrapper.append(link);
        } else {
            wrapper.append(image);
        }

        previewPanel.append(wrapper);
    }

    // --------------------------------------------------
    // Preview: Description
    // --------------------------------------------------

    function appendInlineMarkdown(parent, text) {
        const pattern =
            /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)|\*\*(.+?)\*\*|~~(.+?)~~|`([^`]+)`|\*([^\*\n]+)\*/g;

        let lastIndex = 0;
        let match;

        while ((match = pattern.exec(text)) !== null) {
            if (match.index > lastIndex) {
                parent.append(
                    document.createTextNode(
                        text.slice(lastIndex, match.index)
                    )
                );
            }

            if (match[1] !== undefined) {
                const safeUrl = getSafeUrl(match[2]);

                if (safeUrl) {
                    const link = document.createElement('a');

                    link.href = safeUrl;
                    link.target = '_blank';
                    link.rel = 'noopener noreferrer';
                    link.textContent = match[1];

                    parent.append(link);
                } else {
                    parent.append(
                        document.createTextNode(match[0])
                    );
                }
            } else if (match[3] !== undefined) {
                const strong = document.createElement('strong');

                strong.textContent = match[3];
                parent.append(strong);
            } else if (match[4] !== undefined) {
                const deleted = document.createElement('del');

                deleted.textContent = match[4];
                parent.append(deleted);
            } else if (match[5] !== undefined) {
                const code = document.createElement('code');

                code.textContent = match[5];
                parent.append(code);
            } else if (match[6] !== undefined) {
                const italic = document.createElement('em');

                italic.textContent = match[6];
                parent.append(italic);
            }

            lastIndex = pattern.lastIndex;
        }

        if (lastIndex < text.length) {
            parent.append(
                document.createTextNode(text.slice(lastIndex))
            );
        }
    }

    function renderDescriptionPreview() {
        const description = getDescription();

        if (!description) return;

        const wrapper = document.createElement('div');

        wrapper.className =
            `readme-description-preview align-${descriptionState.alignment}`;

        description.split('\n').forEach((line, index) => {
            if (index > 0) {
                wrapper.append(document.createElement('br'));
            }

            appendInlineMarkdown(wrapper, line);
        });

        previewPanel.append(wrapper);
    }

    // --------------------------------------------------
    // Build Markdown in Canvas Order
    // --------------------------------------------------

    function getDocumentMarkdown() {
        return getFields()
            .map((field) => {
                switch (field.dataset.fieldType) {
                    case 'project-name':
                        return getTextMarkdown();

                    case 'banner':
                        return getBannerMarkdown();

                    case 'description':
                        return getDescriptionMarkdown();

                    default:
                        return '';
                }
            })
            .filter(Boolean)
            .join('\n\n');
    }

    // --------------------------------------------------
    // Render Complete Document
    // --------------------------------------------------

    function renderDocument() {
        previewPanel.replaceChildren();

        const fields = getFields();
        const populatedFields = fields.filter(isFieldPopulated);

        if (populatedFields.length === 0) {
            renderEmptyPreview();
        } else {
            populatedFields.forEach((field) => {
                switch (field.dataset.fieldType) {
                    case 'project-name':
                        renderTextPreview();
                        break;

                    case 'banner':
                        renderBannerPreview();
                        break;

                    case 'description':
                        renderDescriptionPreview();
                        break;
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
    // Project Name Events
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
            const alignment = getAlignment(button.dataset.value);

            textState.alignment = alignment;

            alignmentButtons.forEach((item) => {
                const active = item.dataset.value === alignment;

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
    // Banner Events
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
            const alignment = getAlignment(button.dataset.value);

            bannerState.alignment = alignment;

            bannerAlignmentButtons.forEach((item) => {
                const active = item.dataset.value === alignment;

                item.classList.toggle('is-active', active);
                item.setAttribute('aria-pressed', String(active));
            });

            renderDocument();
        });
    });

    // --------------------------------------------------
    // Description Events
    // --------------------------------------------------

    if (descriptionInput) {
        descriptionInput.addEventListener('input', renderDocument);
        descriptionInput.addEventListener('change', renderDocument);
    }

    const descriptionAlignmentButtons = builder.querySelectorAll(
        '[data-description-setting="alignment"][data-value]'
    );

    descriptionAlignmentButtons.forEach((button) => {
        button.addEventListener('click', () => {
            const alignment = getAlignment(button.dataset.value);

            descriptionState.alignment = alignment;

            descriptionAlignmentButtons.forEach((item) => {
                const active = item.dataset.value === alignment;

                item.classList.toggle('is-active', active);
                item.setAttribute('aria-pressed', String(active));
            });

            renderDocument();
        });
    });

    // --------------------------------------------------
    // Description Formatting
    // --------------------------------------------------

    function applyDescriptionFormat(format) {
        if (!descriptionInput) return;

        const start = descriptionInput.selectionStart;
        const end = descriptionInput.selectionEnd;

        if (start === end) {
            descriptionInput.focus();
            return;
        }

        const value = descriptionInput.value;
        const selectedText = value.slice(start, end);

        // Open the custom modal instead of using prompt().
        if (format === 'link') {
            openLinkModal(start, end, selectedText);
            return;
        }

        const formats = {
            bold: {
                prefix: '**',
                suffix: '**'
            },
            italic: {
                prefix: '*',
                suffix: '*'
            },
            strike: {
                prefix: '~~',
                suffix: '~~'
            },
            code: {
                prefix: '`',
                suffix: '`'
            }
        };

        const definition = formats[format];

        if (!definition) return;

        const { prefix, suffix } = definition;

        const alreadyFormatted =
            selectedText.startsWith(prefix) &&
            selectedText.endsWith(suffix) &&
            selectedText.length >= prefix.length + suffix.length;

        let replacement;
        let selectionStart;
        let selectionEnd;

        if (alreadyFormatted) {
            replacement = selectedText.slice(
                prefix.length,
                selectedText.length - suffix.length
            );

            selectionStart = start;
            selectionEnd = start + replacement.length;
        } else {
            replacement = `${prefix}${selectedText}${suffix}`;
            selectionStart = start + prefix.length;
            selectionEnd = selectionStart + selectedText.length;
        }

        descriptionInput.setRangeText(
            replacement,
            start,
            end,
            'select'
        );

        descriptionInput.focus();

        descriptionInput.setSelectionRange(
            selectionStart,
            selectionEnd
        );

        renderDocument();
    }

    const descriptionFormatButtons = builder.querySelectorAll(
        '[data-description-format]'
    );

    descriptionFormatButtons.forEach((button) => {
        button.addEventListener('click', () => {
            applyDescriptionFormat(button.dataset.descriptionFormat);
        });
    });

    // --------------------------------------------------
    // Clear and Reorder Components
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

                    textState.tag = 'h1';
                    textState.alignment = 'left';
                    textState.bold = false;
                    textState.italic = false;
                    textState.underline = false;
                    textState.strikethrough = false;

                    if (headingSelect) {
                        headingSelect.value = 'h1';
                    }

                    alignmentButtons.forEach((item) => {
                        const active = item.dataset.value === 'left';

                        item.classList.toggle('is-active', active);
                        item.setAttribute('aria-pressed', String(active));
                    });

                    styleButtons.forEach((item) => {
                        const setting = item.dataset.fieldSetting;

                        item.classList.remove('is-active');

                        item.setAttribute(
                            'aria-pressed',
                            String(Boolean(textState[setting]))
                        );
                    });
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

                if (fieldType === 'description' && descriptionInput) {
                    descriptionInput.value = '';
                    descriptionState.alignment = 'left';

                    descriptionAlignmentButtons.forEach((item) => {
                        const active = item.dataset.value === 'left';

                        item.classList.toggle('is-active', active);
                        item.setAttribute('aria-pressed', String(active));
                    });
                }

                renderDocument();

                const firstInput = field.querySelector('[data-field-input]');
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
                canvas.insertBefore(fields[index + 1], field);
                renderDocument();
            }
        });
    });

    // --------------------------------------------------
    // Component Navigation
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
    // Initial Render
    // --------------------------------------------------

    renderDocument();
    activateView('edit');
});