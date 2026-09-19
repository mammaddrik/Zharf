const ZharfPasswordStrength = {
    init() {
        const components = document.querySelectorAll('[data-password-strength]');

        if (!components.length) {
            return;
        }

        components.forEach((component) => {
            this.bind(component);
        });
    },

    bind(component) {
        const passwordInput = component
            .closest('form')
            ?.querySelector(
                'input[name="password"], input[name="new_password1"]'
            );

        if (!passwordInput) {
            return;
        }

        passwordInput.addEventListener('input', () => {
            this.update(component, passwordInput.value);
        });

        this.update(component, passwordInput.value);
    },

    update(component, password) {
        const label = component.querySelector('[data-password-strength-label]');
        const fill = component.querySelector('[data-password-strength-fill]');

        if (!label || !fill) {
            return;
        }

        const criteria = this.getCriteria(password);
        const strength = this.calculate(criteria);

        label.textContent = strength.label;
        fill.style.width = `${strength.percentage}%`;

        this.updateRequirements(component, criteria);
    },

    getCriteria(password) {
        return {
            length: password.length >= 8,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            number: /\d/.test(password),
            special: /[^A-Za-z0-9]/.test(password)
        };
    },

    calculate(criteria) {
        const score = Object.values(criteria).filter(Boolean).length;

        if (score === 0) {
            return {
                label: '',
                percentage: 0
            };
        }

        if (score <= 2) {
            return {
                label: 'Weak',
                percentage: 33
            };
        }

        if (score <= 4) {
            return {
                label: 'Good',
                percentage: 66
            };
        }

        return {
            label: 'Strong',
            percentage: 100
        };
    },

    updateRequirements(component, criteria) {
        Object.entries(criteria).forEach(([name, isValid]) => {
            const requirement = component.querySelector(
                `[data-requirement="${name}"]`
            );

            if (!requirement) {
                return;
            }

            const icon = requirement.querySelector('i');

            requirement.classList.toggle('is-valid', isValid);

            if (!icon) {
                return;
            }

            icon.classList.toggle('bi-circle', !isValid);
            icon.classList.toggle('bi-check-circle-fill', isValid);
        });
    }
};