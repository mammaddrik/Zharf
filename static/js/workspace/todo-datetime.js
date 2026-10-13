document.addEventListener('DOMContentLoaded', () => {
    const fields = document.querySelectorAll('input[name="scheduled_at"]');

    fields.forEach((field) => {
        const now = new Date();
        now.setSeconds(0, 0);

        flatpickr(field, {
            enableTime: true,
            time_24hr: true,
            dateFormat: 'Y-m-d H:i',
            minDate: now,
            minuteIncrement: 5,
            allowInput: false,
            disableMobile: true,

            onReady: (_, __, instance) => {
                const hourInput = instance.hourElement;
                const minuteInput = instance.minuteElement;
                const yearInput = instance.currentYearElement;

                const validateFutureDateTime = () => {
                    const selected = instance.selectedDates[0];

                    if (!selected) {
                        return;
                    }

                    const updated = new Date(selected);
                    updated.setHours(Number(hourInput.value));
                    updated.setMinutes(Number(minuteInput.value));
                    updated.setSeconds(0, 0);

                    const now = new Date();
                    now.setSeconds(0, 0);

                    if (updated < now) {
                        now.setSeconds(0, 0);
                        instance.setDate(now, true);
                    }
                };

                const validateTimeInput = (input, max, getCurrentValue, unit) => {
                    input.removeAttribute('readonly');

                    const correctValue = () => {
                        const rawValue = input.value.trim();
                        const value = Number(rawValue);

                        if (
                            rawValue === '' ||
                            !Number.isInteger(value) ||
                            value < 0 ||
                            value > max
                        ) {
                            const currentValue = getCurrentValue();
                            const selected = instance.selectedDates[0] || new Date();
                            const updated = new Date(selected);

                            if (unit === 'hour') {
                                updated.setHours(currentValue);
                            } else {
                                updated.setMinutes(currentValue);
                            }

                            instance.setDate(updated, false);
                        }

                        validateFutureDateTime();
                    };

                    input.addEventListener('input', () => {
                        const rawValue = input.value.trim();

                        if (rawValue === '') {
                            return;
                        }

                        const value = Number(rawValue);

                        if (
                            Number.isInteger(value) &&
                            (value < 0 || value > max)
                        ) {
                            input.value = String(getCurrentValue()).padStart(2, '0');
                        }
                    }, true);

                    input.addEventListener('blur', correctValue);
                };

                validateTimeInput(
                    hourInput,
                    23,
                    () => new Date().getHours(),
                    'hour'
                );

                validateTimeInput(
                    minuteInput,
                    59,
                    () => new Date().getMinutes(),
                    'minute'
                );

                yearInput.addEventListener('blur', () => {
                    const currentYear = new Date().getFullYear();
                    const year = Number(yearInput.value);

                    if (!Number.isInteger(year) || year < currentYear) {
                        instance.changeYear(currentYear);
                    }

                    validateFutureDateTime();
                });

                instance.config.onChange.push(validateFutureDateTime);
            }
        });
    });
});