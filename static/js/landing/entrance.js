const ZharfEntrance = {
    init() {
        const section = document.querySelector('.entrance-section');

        if (!section) {
            return;
        }

        if (ZharfMotion.prefersReducedMotion()) {
            section.classList.add('is-visible');
            return;
        }

        requestAnimationFrame(() => {
            section.classList.add('is-visible');
        });
    }
};