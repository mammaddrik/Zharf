const ZharfFormSubmit = {
    init() {
        const forms = document.querySelectorAll('form[data-form-submit]');

        if (!forms.length) {
            return;
        }

        forms.forEach((form) => {
            this.bind(form);
        });
    },

    bind(form) {
        form.addEventListener('submit', () => {
            this.start(form);
        });
    },

    start(form) {
        const button = form.querySelector('.authentication-submit');

        if (!button) {
            return;
        }

        button.classList.add('is-loading');
        button.disabled = true;
        button.setAttribute('aria-busy', 'true');
    }
};