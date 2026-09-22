const navigationMenu = document.querySelector('.navigation-menu');
const navigationLinks = document.querySelector('.navigation-links');

if (navigationMenu && navigationLinks) {
    const navigationIcon = navigationMenu.querySelector('.bi');

    navigationMenu.addEventListener('click', function () {
        const isOpen = navigationLinks.classList.toggle('is-open');

        navigationMenu.setAttribute(
            'aria-label',
            isOpen ? 'Close navigation' : 'Open navigation'
        );

        if (navigationIcon) {
            navigationIcon.classList.toggle('bi-list', !isOpen);
            navigationIcon.classList.toggle('bi-x', isOpen);
        }
    });

    const links = navigationLinks.querySelectorAll('a');

    links.forEach(function (link) {
        link.addEventListener('click', function () {
            navigationLinks.classList.remove('is-open');

            navigationMenu.setAttribute(
                'aria-label',
                'Open navigation'
            );

            if (navigationIcon) {
                navigationIcon.classList.remove('bi-x');
                navigationIcon.classList.add('bi-list');
            }
        });
    });
}