const ZharfReveal = {
    init() {
        const sections = document.querySelectorAll('.reveal-section');

        if (!sections.length) {
            return;
        }

        if (ZharfMotion.prefersReducedMotion()) {
            sections.forEach((section) => {
                section.classList.add('is-visible');
            });

            return;
        }

        const observer = new IntersectionObserver(
            (entries, revealObserver) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) {
                        return;
                    }

                    entry.target.classList.add('is-visible');
                    revealObserver.unobserve(entry.target);
                });
            },
            {
                threshold: 0.12,
                rootMargin: '0px 0px -8% 0px'
            }
        );

        sections.forEach((section) => {
            observer.observe(section);
        });
    }
};