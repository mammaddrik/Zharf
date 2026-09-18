const ZharfBackToTop = {
    button: null,

    init() {
        this.button = document.querySelector('.back-to-top');

        if (!this.button) {
            return;
        }

        this.updateVisibility();
        this.bindEvents();
    },

    bindEvents() {
        window.addEventListener('scroll', () => {
            this.updateVisibility();
        }, { passive: true });

        this.button.addEventListener('click', () => {
            const behavior = ZharfMotion.prefersReducedMotion()
                ? 'auto'
                : 'smooth';

            window.scrollTo({
                top: 0,
                behavior
            });
        });
    },

    updateVisibility() {
        const isVisible = window.scrollY > window.innerHeight * 0.6;

        this.button.classList.toggle('is-visible', isVisible);
        this.button.setAttribute('aria-hidden', String(!isVisible));
    }
};