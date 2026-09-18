const ZharfAmbient = {
    init() {
        const ambientElements = document.querySelectorAll(
            '.hero-orbit, .hero-core, .introduction-orbit, .possibility-orbit, .possibility-core, .possibility-particle, .final-cta-orbit, .final-cta-core, .final-cta-particle'
        );

        if (!ambientElements.length) {
            return;
        }

        if (ZharfMotion.prefersReducedMotion()) {
            ambientElements.forEach((element) => {
                element.classList.add('motion-reduced');
            });
        }
    }
};