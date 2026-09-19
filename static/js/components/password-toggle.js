const ZharfPasswordToggle = {
    init() {
        const toggles = document.querySelectorAll('.password-toggle');

        if (!toggles.length) {
            return;
        }

        toggles.forEach((toggle) => {
            toggle.addEventListener('click', () => {
                this.toggle(toggle);
            });
        });
    },

    toggle(toggle) {
        const field = toggle.closest('.password-field');

        if (!field) {
            return;
        }

        const input = field.querySelector('.form-input');
        const icon = toggle.querySelector('i');

        if (!input || !icon) {
            return;
        }

        const isPassword = input.type === 'password';

        input.type = isPassword ? 'text' : 'password';

        toggle.setAttribute(
            'aria-label',
            isPassword ? 'Hide password' : 'Show password'
        );

        toggle.setAttribute(
            'aria-pressed',
            String(isPassword)
        );

        icon.classList.toggle('bi-eye', !isPassword);
        icon.classList.toggle('bi-eye-slash', isPassword);
    }
};