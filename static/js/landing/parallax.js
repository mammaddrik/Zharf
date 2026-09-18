const ZharfParallax = {
    elements: [],
    pointerX: 0,
    pointerY: 0,
    currentX: 0,
    currentY: 0,
    animationFrame: null,

    init() {
        if (ZharfMotion.prefersReducedMotion()) {
            return;
        }

        this.elements = document.querySelectorAll('.parallax-element');

        if (!this.elements.length) {
            return;
        }

        if (window.matchMedia('(hover: none)').matches) {
            return;
        }

        window.addEventListener('pointermove', (event) => {
            this.pointerX = (event.clientX / window.innerWidth - 0.5) * 2;
            this.pointerY = (event.clientY / window.innerHeight - 0.5) * 2;

            if (!this.animationFrame) {
                this.animationFrame = requestAnimationFrame(() => {
                    this.update();
                    this.animationFrame = null;
                });
            }
        });
    },

    update() {
        this.currentX = ZharfMotion.lerp(this.currentX, this.pointerX, 0.06);
        this.currentY = ZharfMotion.lerp(this.currentY, this.pointerY, 0.06);

        this.elements.forEach((element) => {
            const strength = Number(element.dataset.parallaxStrength || 6);
            const x = this.currentX * strength;
            const y = this.currentY * strength;

            element.style.setProperty('--parallax-x', `${x}px`);
            element.style.setProperty('--parallax-y', `${y}px`);
        });

        this.animationFrame = requestAnimationFrame(() => this.update());
    }
};